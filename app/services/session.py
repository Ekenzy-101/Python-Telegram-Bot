import re
from app.services.ai import AIService
from app.services.cache import CacheService
from app.services.email import EmailService
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_LOGS = []
DEFAULT_RATE_LIMIT = {"last_action": None, "count": 0}
DEFAULT_RULES = []
DEFAULT_TEMPLATES = {}
DEFAULT_SETTINGS = {"auto_reply": False, "whitelist": [], "blacklist": []}


class SessionService:
    """Manages user session data"""

    def __init__(self, user_id: int):
        self.ai = AIService()
        self.cache = CacheService(user_id)
        self.gmail = EmailService(user_id)
        self.logs: List[dict] = self.cache.get("logs", DEFAULT_LOGS)
        self.rate_limit = DEFAULT_RATE_LIMIT
        self.rules: List[dict] = self.cache.get("rules", DEFAULT_RULES)
        self.user_id = user_id
        self.templates: Dict[str, dict] = self.cache.get("templates", DEFAULT_TEMPLATES)
        self.settings = self.cache.get("settings", DEFAULT_SETTINGS)

    def delete_all(self):
        """Delete user session data"""
        self.logs = DEFAULT_LOGS
        self.rate_limit = DEFAULT_RATE_LIMIT
        self.rules = DEFAULT_RULES
        self.templates = DEFAULT_TEMPLATES
        self.settings = DEFAULT_SETTINGS
        self.cache.delete("creds")
        self.cache.delete("logs")
        self.cache.delete("rules")
        self.cache.delete("settings")
        self.cache.delete("templates")

    def add_template(self, name: str, content: str, tone: str = "professional"):
        """Add email template"""
        self.templates[name] = {
            "content": content,
            "tone": tone,
            "created": datetime.now().isoformat(),
        }
        self.cache.set("templates", self.templates)

    def delete_template(self, name: str) -> bool:
        """Delete email template"""
        if name in self.templates:
            del self.templates[name]
            self.cache.set("templates", self.templates)
            return True
        return False

    def add_rule(self, rule_type: str, condition: str, action: str):
        """Add automation rule"""
        self.rules.append(
            {
                "type": rule_type,
                "condition": condition,
                "action": action,
                "created": datetime.now().isoformat(),
            }
        )
        self.cache.set("rules", self.rules)

    def log_action(self, action: str, details: dict):
        """Log user action with detailed information"""
        self.logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
            }
        )
        self.cache.set("logs", self.logs)

    def save_settings(self):
        """Save user settings"""
        self.cache.set("settings", self.settings)

    def check_rate_limit(self, max_actions: int = 10, window_seconds: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.now()
        if self.rate_limit["last_action"]:
            time_diff = (now - self.rate_limit["last_action"]).total_seconds()
            if time_diff < window_seconds:
                if self.rate_limit["count"] >= max_actions:
                    return False
                self.rate_limit["count"] += 1
            else:
                self.rate_limit["count"] = 1
                self.rate_limit["last_action"] = now
        else:
            self.rate_limit["last_action"] = now
            self.rate_limit["count"] = 1
        return True

    def process_rules(self, email: dict) -> List[dict]:
        """Process automation rules for an email"""
        applied_actions = []

        for rule in self.rules:
            if self._rule_matches(rule, email):
                action_result = self._apply_rule_action(rule, email)
                if action_result:
                    applied_actions.append(
                        {
                            "rule": rule,
                            "action": action_result,
                            "email_id": email.get("id"),
                        }
                    )
                    self.log_action(
                        "rule_applied",
                        {
                            "rule_type": rule["type"],
                            "rule_condition": rule["condition"],
                            "email_id": email.get("id"),
                            "subject": email.get("subject"),
                        },
                    )

        return applied_actions

    def _rule_matches(self, rule: dict, email: dict) -> bool:
        """Check if a rule matches an email"""
        condition = rule["condition"].lower()
        email_subject = email.get("subject", "").lower()
        email_from = email.get("from", "").lower()
        email_body = email.get("body", "").lower()

        # Simple pattern matching
        if "subject contains" in condition:
            keyword = condition.replace("subject contains", "").strip()
            return keyword in email_subject
        elif "from contains" in condition:
            keyword = condition.replace("from contains", "").strip()
            return keyword in email_from
        elif "body contains" in condition:
            keyword = condition.replace("body contains", "").strip()
            return keyword in email_body
        elif "from" in condition:
            # Exact match
            email_addr = self.gmail.extract_email(email_from)
            return email_addr in condition.lower()

        return False

    def _apply_rule_action(self, rule: dict, email: dict) -> Optional[dict]:
        """Apply a rule action to an email"""
        rule_type = rule["type"]
        action = rule["action"]

        try:
            if rule_type == "label":
                # Extract label name from action
                label_name = action.replace("label as", "").strip()
                if self.gmail and self.gmail.service:
                    success = self.gmail.apply_label(email["id"], label_name)
                    return {"type": "label", "label": label_name, "success": success}

            elif rule_type == "archive":
                if self.gmail and self.gmail.service:
                    success = self.gmail.archive_message(email["id"])
                    return {"type": "archive", "success": success}

            elif rule_type == "reply":
                # Auto-reply using template
                if self.settings.get("auto_reply", False):
                    template_name = action.strip()
                    template = self.templates.get(template_name)
                    if template:
                        reply_text = self.ai.generate_reply(email, template)
                        sender_email = self.gmail.extract_email(email["from"])
                        success = self.gmail.send_reply(
                            email["id"],
                            email["threadId"],
                            reply_text,
                            sender_email,
                            f"Re: {email['subject']}",
                        )
                        return {
                            "type": "reply",
                            "success": success,
                            "template": template_name,
                        }

        except Exception as e:
            self.log_action("rule_error", {"error": str(e), "rule": rule})
            return None

        return None
