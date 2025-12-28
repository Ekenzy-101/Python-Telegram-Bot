import re
from datetime import datetime
from typing import Dict, List, Optional
from app.services.email import EmailService


class SessionService:
    """Manages user session data"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.gmail = EmailService(user_id)
        self.templates: Dict[str, dict] = {}
        self.rules: List[dict] = []
        self.settings = {"auto_reply": False, "whitelist": [], "blacklist": []}
        self.audit_log: List[dict] = []
        self.rate_limit = {"last_action": None, "count": 0}  # Simple rate limiting

    def add_template(self, name: str, content: str, tone: str = "professional"):
        """Add email template"""
        self.templates[name] = {
            "content": content,
            "tone": tone,
            "created": datetime.now().isoformat(),
        }

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

    def log_action(self, action: str, details: dict):
        """Log user action with detailed information"""
        self.audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
                "user_id": self.user_id,
            }
        )
        # Keep only last 100 entries
        if len(self.audit_log) > 100:
            self.audit_log = self.audit_log[-100:]

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

    def process_rules(self, email: dict, ai_service, templates: Dict[str, dict]) -> List[dict]:
        """Process automation rules for an email"""
        applied_actions = []
        
        for rule in self.rules:
            if self._rule_matches(rule, email):
                action_result = self._apply_rule_action(rule, email, ai_service, templates)
                if action_result:
                    applied_actions.append({
                        "rule": rule,
                        "action": action_result,
                        "email_id": email.get("id"),
                    })
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
            email_addr = self._extract_email(email_from)
            return email_addr in condition.lower()
        
        return False

    def _apply_rule_action(self, rule: dict, email: dict, ai_service, templates: Dict[str, dict]) -> Optional[dict]:
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
                if self.settings["auto_reply"]:
                    template_name = action.strip()
                    template = templates.get(template_name)
                    if template and self.gmail and self.gmail.service:
                        reply_text = ai_service.generate_reply(email, template)
                        sender_email = self._extract_email(email["from"])
                        success = self.gmail.send_reply(
                            email["id"],
                            email["threadId"],
                            reply_text,
                            sender_email,
                            f"Re: {email['subject']}",
                        )
                        return {"type": "reply", "success": success, "template": template_name}
        
        except Exception as e:
            self.log_action("rule_error", {"error": str(e), "rule": rule})
            return None
        
        return None

    def _extract_email(self, email_string: str) -> str:
        """Extract email address from string"""
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email_string)
        return match.group(0) if match else email_string.lower()
