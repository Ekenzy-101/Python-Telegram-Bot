"""
Telegram Bot - Personal AI Email Agent for Gmail
Handles email organization, auto-replies, and AI-powered responses
"""

import logging
import re
from app.config import settings
from app.services import AIService, EmailService, SessionService
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.warnings import PTBUserWarning
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from warnings import filterwarnings


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=settings.log_level,
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

# Conversation states
(
    AWAITING_TEMPLATE_NAME,
    AWAITING_TEMPLATE_CONTENT,
    AWAITING_RULE_TYPE,
    AWAITING_RULE_CONDITION,
    AWAITING_RULE_ACTION,
    AWAITING_WHITELIST_EMAIL,
    AWAITING_BLACKLIST_EMAIL,
) = range(7)

# User data structure
user_sessions: Dict[int, SessionService] = {}
ai_service = AIService()


# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = SessionService(user_id)

    text = (
        "🤖 *Personal AI Email Agent*\n\n"
        "I help you manage Gmail with AI-powered automation!\n\n"
        "Features:\n"
        "• Auto-organize emails\n"
        "• Smart reply suggestions\n"
        "• Template-based responses\n"
        "• Custom automation rules\n\n"
        "Choose an option below:"
    )
    keyboard = [
        [InlineKeyboardButton("📧 Connect Gmail", callback_data="connect_gmail")],
        [InlineKeyboardButton("📬 Check Inbox", callback_data="check_inbox")],
        [InlineKeyboardButton("📝 Manage Templates", callback_data="manage_templates")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("📊 Audit Log", callback_data="audit_log")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = user_sessions.get(user_id)
    if not session:
        await query.edit_message_text("Please /start the bot first")
        return

    session.log_action(query.data, {})

    if query.data == "connect_gmail":
        await connect_gmail(update, context)

    elif query.data == "check_inbox":
        await check_inbox(update, context)

    elif query.data == "manage_templates":
        await show_templates(update, context)

    elif query.data == "settings":
        await show_settings(update, context)

    elif query.data == "audit_log":
        await show_audit_log(update, context)

    elif query.data == "main_menu":
        await start(update, context)

    elif query.data == "toggle_auto":
        await toggle_auto_reply(update, context)

    elif query.data == "manage_rules":
        await manage_rules(update, context)

    elif query.data == "add_template":
        await start_add_template(update, context)

    elif query.data == "add_rule":
        await start_add_rule(update, context)

    elif query.data == "view_suggestions":
        await view_reply_suggestions(update, context)

    elif query.data == "manage_whitelist":
        await manage_whitelist(update, context)

    elif query.data == "manage_blacklist":
        await manage_blacklist(update, context)

    elif query.data.startswith("reply_"):
        # Handle reply actions: reply_approve_<message_id>, reply_deny_<message_id>
        parts = query.data.split("_")
        if len(parts) >= 3:
            action = parts[1]
            message_id = "_".join(parts[2:])
            await handle_reply_action(update, context, action, message_id)

    elif query.data.startswith("template_"):
        # Handle template actions: template_delete_<name>, template_use_<name>
        parts = query.data.split("_", 2)
        if len(parts) >= 3:
            action = parts[1]
            template_name = parts[2]
            await handle_template_action(update, context, action, template_name)

    elif query.data.startswith("rule_"):
        # Handle rule actions: rule_delete_<index>
        parts = query.data.split("_", 2)
        if len(parts) >= 3:
            action = parts[1]
            rule_index = int(parts[2])
            await handle_rule_action(update, context, action, rule_index)

    elif query.data.startswith("email_"):
        # Handle email actions: email_archive_<id>, email_label_<id>
        parts = query.data.split("_", 2)
        if len(parts) >= 3:
            action = parts[1]
            email_id = parts[2]
            await handle_email_action(update, context, action, email_id)

    elif query.data.startswith("add_whitelist"):
        await start_add_whitelist(update, context)

    elif query.data.startswith("add_blacklist"):
        await start_add_blacklist(update, context)

    elif query.data.startswith("remove_whitelist_"):
        email = query.data.replace("remove_whitelist_", "")
        await remove_whitelist(update, context, email)

    elif query.data.startswith("remove_blacklist_"):
        email = query.data.replace("remove_blacklist_", "")
        await remove_blacklist(update, context, email)


async def connect_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Connect to gmail"""
    query = update.callback_query
    state = f"{update.effective_user.id}:{update.effective_chat.id}"
    text = "❌ Error: Could not generate authentication URL. Please try again later."
    url = EmailService(update.effective_user.id).start_auth(state)
    if not url:
        await query.edit_message_text(text, parse_mode="Markdown")
        return

    text = "Please authenticate with Google to use this bot"
    keyboard = [
        [InlineKeyboardButton("📧 Connect Gmail Account", url=url)],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def check_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check inbox and display messages with AI analysis"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email_service = EmailService(user_id)

    # Check if user is authenticated
    if not email_service.creds:
        await query.edit_message_text(
            "❌ Please connect your Gmail account first.",
            parse_mode="Markdown",
        )
        return

    await query.edit_message_text("⏳ Analyzing your inbox...", parse_mode="Markdown")

    # Check rate limit
    if not session.check_rate_limit(max_actions=20, window_seconds=60):
        await query.edit_message_text(
            "⏸️ Rate limit exceeded. Please wait a moment before checking again.",
            parse_mode="Markdown",
        )
        return

    messages = email_service.get_inbox_messages(max_results=10)

    if not messages:
        text = "📬 *Inbox Summary*\n\nNo new messages found."
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="check_inbox")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode="Markdown"
        )
        return

    text = "📬 *Inbox Summary*\n\n"
    urgent_count = 0
    actionable_items = []

    for i, msg in enumerate(messages[:5], 1):  # Show top 5
        # Check whitelist/blacklist
        sender_email = _extract_email(msg["from"])
        if sender_email in session.settings["blacklist"]:
            continue
        if sender_email in session.settings["whitelist"]:
            msg["priority"] = "high"

        # AI analysis
        analysis = ai_service.analyze_email(msg)
        category = analysis.get("category", "general")
        sentiment = analysis.get("sentiment", "neutral")
        topics = analysis.get("key_topics", "")
        suggested_action = analysis.get("suggested_action", "")

        # Categorize
        if category == "urgent":
            urgent_count += 1
            emoji = "🔴"
        elif category == "follow-up":
            emoji = "🟡"
        elif category == "spam":
            emoji = "⚫"
        elif category == "invoice":
            emoji = "💰"
        else:
            emoji = "📧"

        text += f"{emoji} *{i}. {msg['subject'][:50]}*\n"
        text += f"   From: {msg['from'][:40]}\n"
        text += f"   Category: {category.upper()}\n"
        if topics:
            text += f"   Topics: {topics[:30]}\n"
        text += f"   Preview: {msg['snippet'][:60]}...\n\n"

        # Store actionable items
        if category in ["urgent", "follow-up"] or suggested_action:
            actionable_items.append(
                {
                    "id": msg["id"],
                    "subject": msg["subject"],
                    "from": msg["from"],
                    "category": category,
                    "suggested_action": suggested_action,
                }
            )

    text += f"\n*Summary:* {urgent_count} urgent, {len(actionable_items)} actionable"

    keyboard = []
    if actionable_items:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "💡 View Reply Suggestions", callback_data="view_suggestions"
                )
            ]
        )
    keyboard.extend(
        [
            [InlineKeyboardButton("🔄 Refresh", callback_data="check_inbox")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Process automation rules (rules are processed regardless of auto_reply setting)
    # Auto_reply setting only controls whether replies are sent automatically
    if session.rules:
        for msg in messages:
            # Only process rules if not blacklisted
            sender_email = _extract_email(msg["from"])
            if sender_email not in session.settings["blacklist"]:
                applied_actions = session.process_rules(
                    msg, ai_service, session.templates
                )
                if applied_actions:
                    logger.info(
                        f"Applied {len(applied_actions)} rules to message {msg['id']}"
                    )

    # Store actionable items in context
    context.user_data["actionable_items"] = actionable_items
    context.user_data["messages"] = messages

    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def show_templates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show email templates"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    text = "📝 *Email Templates*\n\n"
    if session.templates:
        for name, template in session.templates.items():
            text += f"• *{name}*\n"
            text += f"  {template['content'][:50]}...\n"
            text += f"  Tone: {template.get('tone', 'professional')}\n\n"
    else:
        text += "No templates yet. Create one below."

    keyboard = [
        [InlineKeyboardButton("➕ Add Template", callback_data="add_template")],
    ]
    if session.templates:
        for name in session.templates.keys():
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"❌ Delete {name[:20]}",
                        callback_data=f"template_delete_{name}",
                    )
                ]
            )
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    auto_status = "✅ ON" if session.settings["auto_reply"] else "❌ OFF"
    text = f"""⚙️ *Settings*

Auto-Reply: {auto_status}
Whitelisted: {len(session.settings['whitelist'])} senders
Blacklisted: {len(session.settings['blacklist'])} senders

Rules: {len(session.rules)} active"""

    keyboard = [
        [InlineKeyboardButton("🔄 Toggle Auto-Reply", callback_data="toggle_auto")],
        [InlineKeyboardButton("📋 Manage Rules", callback_data="manage_rules")],
        [
            InlineKeyboardButton("✅ Whitelist", callback_data="manage_whitelist"),
            InlineKeyboardButton("🚫 Blacklist", callback_data="manage_blacklist"),
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def show_audit_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show audit log"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    text = "📊 *Audit Log*\n\n"
    if session.audit_log:
        for entry in session.audit_log[-10:]:
            timestamp = entry.get("timestamp", "")[:16]  # Format timestamp
            action = entry.get("action", "")
            details = entry.get("details", {})

            text += f"• *{timestamp}*\n"
            text += f"  Action: {action}\n"
            if details:
                for key, value in details.items():
                    text += f"  {key}: {value}\n"
            text += "\n"
    else:
        text += "No actions logged yet"

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


def _extract_email(email_string: str) -> str:
    """Extract email address from 'Name <email@domain.com>' format"""
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email_string)
    return match.group(0) if match else email_string.lower()


async def toggle_auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle auto-reply setting"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    session.settings["auto_reply"] = not session.settings["auto_reply"]
    session.log_action(
        "toggle_auto_reply",
        {"auto_reply": session.settings["auto_reply"]},
    )

    await show_settings(update, context)


async def manage_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show and manage automation rules"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    text = "📋 *Automation Rules*\n\n"
    if session.rules:
        for i, rule in enumerate(session.rules):
            text += f"*{i+1}. {rule['type']}*\n"
            text += f"   Condition: {rule['condition']}\n"
            text += f"   Action: {rule['action']}\n\n"
    else:
        text += "No rules configured yet.\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Rule", callback_data="add_rule")],
    ]
    if session.rules:
        for i, rule in enumerate(session.rules):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"❌ Delete Rule {i+1}", callback_data=f"rule_delete_{i}"
                    )
                ]
            )
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def start_add_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start template creation conversation"""
    query = update.callback_query
    await query.edit_message_text(
        "📝 *Add Template*\n\nPlease send the template name:",
        parse_mode="Markdown",
    )
    return AWAITING_TEMPLATE_NAME


async def start_add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start rule creation conversation"""
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("Auto Label", callback_data="rule_type_label"),
            InlineKeyboardButton("Auto Reply", callback_data="rule_type_reply"),
        ],
        [InlineKeyboardButton("Auto Archive", callback_data="rule_type_archive")],
        [InlineKeyboardButton("Cancel", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "📋 *Add Rule*\n\nSelect rule type:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return AWAITING_RULE_TYPE


async def view_reply_suggestions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show reply suggestions for actionable emails"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email_service = EmailService(user_id)

    actionable_items = context.user_data.get("actionable_items", [])
    messages = context.user_data.get("messages", [])

    if not actionable_items:
        await query.edit_message_text(
            "No actionable items found.", parse_mode="Markdown"
        )
        return

    # Show first actionable item with reply suggestion
    item = actionable_items[0]
    message = next((m for m in messages if m["id"] == item["id"]), None)

    if not message:
        await query.edit_message_text("Message not found.", parse_mode="Markdown")
        return

    # Generate reply suggestion
    if session.templates:
        # Use first template or best matching template
        template_name = list(session.templates.keys())[0]
        template = session.templates[template_name]
        reply_text = ai_service.generate_reply(message, template)
    else:
        # Generate without template
        reply_text = ai_service.generate_reply(
            message,
            {"content": "Thank you for your email. I will get back to you soon."},
        )

    text = f"💡 *Reply Suggestion*\n\n"
    text += f"*To:* {message['from']}\n"
    text += f"*Subject:* {message['subject']}\n\n"
    text += f"*Suggested Reply:*\n{reply_text[:500]}\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve & Send", callback_data=f"reply_approve_{message['id']}"
            ),
            InlineKeyboardButton(
                "❌ Deny", callback_data=f"reply_deny_{message['id']}"
            ),
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store reply text in context
    context.user_data[f"reply_{message['id']}"] = reply_text
    context.user_data[f"message_{message['id']}"] = message

    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_reply_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, message_id: str
):
    """Handle reply approval/denial"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email_service = EmailService(user_id)

    message = context.user_data.get(f"message_{message_id}")
    reply_text = context.user_data.get(f"reply_{message_id}")

    if not message or not reply_text:
        await query.answer("Error: Message data not found", show_alert=True)
        return

    if action == "approve":
        # Check rate limit
        if not session.check_rate_limit(max_actions=5, window_seconds=60):
            await query.answer("⏸️ Rate limit exceeded. Please wait.", show_alert=True)
            return

        # Extract sender email
        sender_email = _extract_email(message["from"])

        # Check blacklist
        if sender_email in session.settings["blacklist"]:
            await query.answer("❌ Sender is blacklisted", show_alert=True)
            return

        # Send reply
        success = email_service.send_reply(
            message_id,
            message["threadId"],
            reply_text,
            sender_email,
            f"Re: {message['subject']}",
        )

        if success:
            session.log_action(
                "reply_sent",
                {
                    "message_id": message_id,
                    "to": sender_email,
                    "subject": message["subject"],
                },
            )
            await query.answer("✅ Reply sent successfully!", show_alert=True)
            await query.edit_message_text(
                "✅ *Reply Sent*\n\nYour reply has been sent successfully.",
                parse_mode="Markdown",
            )
        else:
            await query.answer("❌ Failed to send reply", show_alert=True)
    else:  # deny
        session.log_action(
            "reply_denied",
            {"message_id": message_id, "subject": message["subject"]},
        )
        await query.answer("Reply suggestion denied", show_alert=False)
        await query.edit_message_text("Reply suggestion denied.", parse_mode="Markdown")


async def handle_template_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, template_name: str
):
    """Handle template actions (delete, use)"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    if action == "delete":
        if template_name in session.templates:
            del session.templates[template_name]
            session.log_action("template_deleted", {"name": template_name})
            await query.answer("Template deleted", show_alert=False)
            await show_templates(update, context)
        else:
            await query.answer("Template not found", show_alert=True)


async def handle_rule_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, rule_index: int
):
    """Handle rule actions (delete)"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    if action == "delete":
        if 0 <= rule_index < len(session.rules):
            rule = session.rules.pop(rule_index)
            session.log_action("rule_deleted", {"rule": rule})
            await query.answer("Rule deleted", show_alert=False)
            await manage_rules(update, context)
        else:
            await query.answer("Rule not found", show_alert=True)


async def handle_email_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE, action: str, email_id: str
):
    """Handle email actions (archive, label)"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email_service = EmailService(user_id)

    if action == "archive":
        success = email_service.archive_message(email_id)
        if success:
            session.log_action("email_archived", {"message_id": email_id})
            await query.answer("✅ Email archived", show_alert=False)
        else:
            await query.answer("❌ Failed to archive", show_alert=True)
    elif action == "label":
        # This would need a label selection UI, simplified for now
        await query.answer("Label feature - coming soon", show_alert=False)


async def manage_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage whitelist"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    text = "✅ *Whitelist*\n\n"
    if session.settings["whitelist"]:
        for email in session.settings["whitelist"]:
            text += f"• {email}\n"
    else:
        text += "No whitelisted senders.\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Email", callback_data="add_whitelist")],
    ]
    if session.settings["whitelist"]:
        for email in session.settings["whitelist"]:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"❌ Remove {email[:20]}",
                        callback_data=f"remove_whitelist_{email}",
                    )
                ]
            )
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def manage_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage blacklist"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    text = "🚫 *Blacklist*\n\n"
    if session.settings["blacklist"]:
        for email in session.settings["blacklist"]:
            text += f"• {email}\n"
    else:
        text += "No blacklisted senders.\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Email", callback_data="add_blacklist")],
    ]
    if session.settings["blacklist"]:
        for email in session.settings["blacklist"]:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"❌ Remove {email[:20]}",
                        callback_data=f"remove_blacklist_{email}",
                    )
                ]
            )
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def start_add_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start whitelist addition"""
    query = update.callback_query
    await query.edit_message_text(
        "📧 *Add to Whitelist*\n\nSend the email address to whitelist:",
        parse_mode="Markdown",
    )
    return AWAITING_WHITELIST_EMAIL


async def start_add_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start blacklist addition"""
    query = update.callback_query
    await query.edit_message_text(
        "🚫 *Add to Blacklist*\n\nSend the email address to blacklist:",
        parse_mode="Markdown",
    )
    return AWAITING_BLACKLIST_EMAIL


# Conversation handlers
async def receive_template_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive template name"""
    template_name = update.message.text
    context.user_data["template_name"] = template_name
    await update.message.reply_text(
        f"Template name: *{template_name}*\n\nNow send the template content:",
        parse_mode="Markdown",
    )
    return AWAITING_TEMPLATE_CONTENT


async def receive_template_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive template content"""
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    template_name = context.user_data.get("template_name")
    template_content = update.message.text

    session.add_template(template_name, template_content)
    session.log_action("template_added", {"name": template_name})

    await update.message.reply_text(
        f"✅ Template *{template_name}* added successfully!",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def receive_rule_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive rule type from callback"""
    query = update.callback_query
    await query.answer()

    rule_type = query.data.replace("rule_type_", "")
    context.user_data["rule_type"] = rule_type

    await query.edit_message_text(
        f"Rule type: *{rule_type}*\n\nSend the condition (e.g., 'subject contains invoice'):",
        parse_mode="Markdown",
    )
    return AWAITING_RULE_CONDITION


async def receive_rule_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive rule condition"""
    condition = update.message.text
    context.user_data["rule_condition"] = condition

    rule_type = context.user_data.get("rule_type", "label")
    if rule_type == "reply":
        await update.message.reply_text(
            f"Condition: *{condition}*\n\nSend the template name to use for auto-reply:",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"Condition: *{condition}*\n\nSend the action (e.g., 'label as Important'):",
            parse_mode="Markdown",
        )
    return AWAITING_RULE_ACTION


async def receive_rule_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive rule action"""
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    action = update.message.text
    rule_type = context.user_data.get("rule_type", "label")
    condition = context.user_data.get("rule_condition", "")

    session.add_rule(rule_type, condition, action)
    session.log_action(
        "rule_added", {"type": rule_type, "condition": condition, "action": action}
    )

    await update.message.reply_text(
        f"✅ Rule added successfully!",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def receive_whitelist_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive whitelist email"""
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email = _extract_email(update.message.text)

    if email not in session.settings["whitelist"]:
        session.settings["whitelist"].append(email)
        session.log_action("whitelist_added", {"email": email})
        await update.message.reply_text(
            f"✅ {email} added to whitelist!",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"Email already in whitelist.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END


async def receive_blacklist_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive blacklist email"""
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    email = _extract_email(update.message.text)

    if email not in session.settings["blacklist"]:
        session.settings["blacklist"].append(email)
        session.log_action("blacklist_added", {"email": email})
        await update.message.reply_text(
            f"✅ {email} added to blacklist!",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"Email already in blacklist.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END


async def remove_whitelist(
    update: Update, context: ContextTypes.DEFAULT_TYPE, email: str
):
    """Remove email from whitelist"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    if email in session.settings["whitelist"]:
        session.settings["whitelist"].remove(email)
        session.log_action("whitelist_removed", {"email": email})
        await query.answer("Removed from whitelist", show_alert=False)
    await manage_whitelist(update, context)


async def remove_blacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE, email: str
):
    """Remove email from blacklist"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = user_sessions[user_id]

    if email in session.settings["blacklist"]:
        session.settings["blacklist"].remove(email)
        session.log_action("blacklist_removed", {"email": email})
        await query.answer("Removed from blacklist", show_alert=False)
    await manage_blacklist(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


def new():
    """Main function to run the bot"""
    app = (
        Application.builder()
        .updater(None)
        .token(settings.telegram_bot_token)
        .read_timeout(10)
        .get_updates_read_timeout(45)
        .build()
    )

    # Template conversation handler
    template_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_template, pattern="^add_template$")
        ],
        states={
            AWAITING_TEMPLATE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_template_name)
            ],
            AWAITING_TEMPLATE_CONTENT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, receive_template_content
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Rule conversation handler
    rule_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_rule, pattern="^add_rule$")],
        states={
            AWAITING_RULE_TYPE: [
                CallbackQueryHandler(receive_rule_type, pattern="^rule_type_")
            ],
            AWAITING_RULE_CONDITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rule_condition)
            ],
            AWAITING_RULE_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_rule_action)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Whitelist conversation handler
    whitelist_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_whitelist, pattern="^add_whitelist$")
        ],
        states={
            AWAITING_WHITELIST_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_whitelist_email)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Blacklist conversation handler
    blacklist_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_blacklist, pattern="^add_blacklist$")
        ],
        states={
            AWAITING_BLACKLIST_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_blacklist_email)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(template_conv)
    app.add_handler(rule_conv)
    app.add_handler(whitelist_conv)
    app.add_handler(blacklist_conv)
    app.add_handler(CallbackQueryHandler(button_callback))
    return app
