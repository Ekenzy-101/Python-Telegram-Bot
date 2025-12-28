# 🤖 Kenzy Mail AI

> Your Personal AI Email Agent for Gmail - Powered by Claude AI & Telegram

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)](https://developers.google.com/gmail/api)
[![Anthropic Claude](https://img.shields.io/badge/Anthropic-Claude-purple.svg)](https://www.anthropic.com/)

Kenzy Mail AI is an intelligent Telegram bot that transforms how you manage your Gmail inbox. Using advanced AI from Anthropic's Claude, it automatically organizes emails, suggests smart replies, and handles routine email tasks - all through a simple chat interface.

---

## ✨ Features

### 🎯 Core Capabilities

- **🔐 Secure Gmail Integration** - OAuth2 authentication for safe, authorized access
- **🤖 AI-Powered Email Analysis** - Claude AI categorizes and prioritizes your emails
- **📝 Smart Reply Generation** - Context-aware responses using custom templates
- **⚡ Auto-Reply System** - Automated responses based on your rules
- **🏷️ Intelligent Organization** - Auto-label and archive emails by category
- **📊 Real-Time Inbox Summary** - See urgent emails at a glance

### 🛠️ Advanced Features

- **📋 Custom Email Templates** - Create reusable response templates with variables
- **⚙️ Automation Rules** - "If email from X, then label Y and reply with Z"
- **🎨 Template Variables** - Dynamic placeholders: `{sender_name}`, `{subject}`, `{date}`
- **📈 Audit Trail** - Complete log of all bot actions and decisions
- **🔒 Whitelist/Blacklist** - Control who gets auto-responses
- **⏱️ Rate Limiting** - Prevents spam and respects Gmail quotas
- **🔍 Email Search** - Find emails by sender, subject, or keywords

---

## 🎬 Demo

```
User: /start

Kenzy: 🤖 Personal AI Email Agent

I help you manage Gmail with AI-powered automation!

Features:
• Auto-organize emails
• Smart reply suggestions
• Template-based responses
• Custom automation rules

[📧 Connect Gmail] [📬 Check Inbox]

---

User: *clicks Check Inbox*

Kenzy: 📬 Inbox Summary

1. From: client@example.com
   Subject: Project Update Needed
   Preview: Can you provide an update on the project...
   Category: urgent 🔴

2. From: newsletter@tech.com
   Subject: Weekly Tech News
   Preview: This week's top stories...
   Category: newsletter 📰

[💬 Reply to #1] [🗑️ Archive #2]
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account
- Telegram account
- Google Cloud Platform account (free tier)
- Anthropic API key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Ekenzy-101/Python-Telegram-Bot.git
   cd Python-Telegram-Bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials**

   - Follow the [Authentication Guide](docs/AUTHENTICATION.md)
   - Download `credentials.json` to project root

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

5. **Run the bot**
   ```bash
   fastapi dev app/app.py
   ```

---

## 📋 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Telegram (get from @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_URL=https://domain.com/webhook

# Anthropic API Key (get from console.anthropic.com)
OPENAI_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_URL=https://api.anthropic.com/v1/
OPENAI_MODEL=claude-sonnet-4-20250514

# Redis
REDIS_URL=

# Optional: Rate Limiting
MAX_EMAILS_PER_HOUR=50
MAX_REPLIES_PER_DAY=100
```

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Kenzy Mail AI"
3. Enable the Gmail API
4. Configure OAuth consent screen:
   - User Type: External
   - Scopes: `https://www.googleapis.com/auth/gmail.modify`
   - Test users: Add your Gmail address
5. Create OAuth 2.0 credentials:
   - Application type: Web app
   - Download JSON as `credentials.json`

Detailed instructions: [docs/GOOGLE_CLOUD_SETUP.md](docs/GOOGLE_CLOUD_SETUP.md)

### Telegram Bot Setup

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name: `Kenzy Mail AI`
4. Choose a username: `kenzy_mail_bot` (must end in 'bot')
5. Copy the token to your `.env` file

### Anthropic API Key

1. Sign up at [console.anthropic.com](https://console.anthropic.com/)
2. Navigate to API Keys
3. Create a new key
4. Copy to your `.env` file

---

## 📖 Usage Guide

### Basic Commands

- `/start` - Initialize the bot and show main menu
- `/inbox` - Check your inbox for new emails
- `/templates` - Manage email templates
- `/rules` - Configure automation rules
- `/settings` - Adjust bot preferences
- `/help` - Show help information
- `/stats` - View usage statistics

### Creating Email Templates

1. Click "📝 Manage Templates"
2. Click "➕ Add Template"
3. Enter template name: `meeting_followup`
4. Enter template content:

   ```
   Hi {sender_name},

   Thank you for the meeting on {date}. I'll review the materials
   you shared and get back to you by end of week.

   Best regards,
   Your Name
   ```

5. Template saved! Use it for quick replies

### Setting Up Auto-Reply Rules

1. Go to "⚙️ Settings" → "📋 Manage Rules"
2. Click "➕ Add Rule"
3. Configure rule:
   - **Trigger:** When email from `*@client.com`
   - **Action:** Apply label "Client" and reply with template "client_response"
   - **Auto-send:** Yes (or No for approval mode)

### Workflow Example

```
1. New email arrives from client@company.com
   ↓
2. Kenzy analyzes email with Claude AI
   - Category: "business"
   - Sentiment: "neutral"
   - Priority: "high"
   ↓
3. Applies your rule:
   - Labels email as "Client"
   - Generates reply from template
   ↓
4. Telegram notification:
   "📧 New email from client@company.com
    Subject: Q4 Project Review

    🤖 AI Suggested Reply:
    [Preview of generated response]

    [✅ Send] [✏️ Edit] [❌ Skip]"
   ↓
5. You approve → Email sent automatically
```

---

## 🏗️ Project Structure

```

kenzy-mail-ai/
├── app
│   ├── app.py
│   ├── bot.py
│   ├── config.py
│   ├── __init__.py
│   ├── __pycache__
│   ├── services
│   │   ├── ai.py
│   │   ├── email.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── session.py
│   └── test.py
├── icon.png
├── logo.png
├── README.md
└── requirements.txt
```

---

## 🔒 Security & Privacy

### Data Protection

- **No Email Storage:** Emails are processed in real-time, never stored on our servers
- **OAuth2 Security:** Uses Google's secure authentication, no password storage
- **Encrypted Tokens:** User tokens encrypted at rest
- **Local Processing:** All AI processing happens via secure API calls

### Permissions

Kenzy Mail AI requests the following Gmail permissions:

- `gmail.modify` - Read, send, label, and organize emails
- **Does NOT request:** Delete emails permanently, access other Google services

### Privacy Policy

- We never share your email data with third parties
- Anthropic's Claude processes email content following their [privacy policy](https://www.anthropic.com/privacy)
- You can revoke access anytime in [Google Account Settings](https://myaccount.google.com/permissions)

### Best Practices

1. Never share your `credentials.json` or `token.json`
2. Use environment variables for sensitive data
3. Enable 2FA on your Google account
4. Regularly review bot activity in audit logs
5. Set up whitelist for auto-reply to prevent spam

---

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📊 Roadmap

### Version 1.0 (Current)

- ✅ Gmail OAuth2 integration
- ✅ Basic email reading and sending
- ✅ AI-powered email analysis
- ✅ Template system
- ✅ Auto-reply rules
- ✅ Telegram bot interface

### Version 1.1 (Coming Soon)

- 🔲 Multi-user support with database
- 🔲 Advanced filtering and search
- 🔲 Email scheduling (send later)
- 🔲 Attachment handling
- 🔲 Email thread management
- 🔲 Analytics dashboard

### Version 2.0 (Future)

- 🔲 Multi-account support
- 🔲 Mobile app (React Native)
- 🔲 Calendar integration
- 🔲 Smart meeting scheduling
- 🔲 Email insights and trends
- 🔲 Integration with other email providers

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Kenzy Mail AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## ⭐ Show Your Support

If Kenzy Mail AI helps you manage your emails better, please consider:

- ⭐ Starring the repository
- 🐦 Sharing on Twitter
- 🤝 Contributing to the project

---
