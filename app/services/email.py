import base64
from datetime import datetime
import logging
import re
from app.services.cache import CacheService
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Optional


logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class EmailService:
    """Manages Gmail API operations"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cache = CacheService(user_id)
        self.creds = self._read_user_creds()
        if self.creds:
            self.service = build("gmail", "v1", credentials=self.creds)
        else:
            self.service = None

    def start_auth(self, state: str) -> str:
        """Generates authorization url with Google using OAuth2"""
        try:
            flow = self._create_auth_flow()
            authorization_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
                state=state,
            )
            return authorization_url
        except Exception as e:
            logger.error(f"Failed to start authentication: {e}")
            return ""

    def end_auth(self, code: str) -> bool:
        """Validates Authenticate with Gmail using OAuth2"""
        try:
            flow = self._create_auth_flow()
            flow.fetch_token(code=code)
            self.creds = flow.credentials
            self.service = build("gmail", "v1", credentials=self.creds)
            self.cache.set("creds", self.creds.to_json())
            return True
        except Exception as e:
            logger.error(f"Failed to end authentication: {e}")
            return False

    def get_inbox_messages(
        self, max_results: int = 10, label_ids: List[str] = None
    ) -> List[dict]:
        """Fetch inbox messages"""
        try:
            if not self.service:
                return []

            query_params = {"userId": "me", "maxResults": max_results}
            if label_ids:
                query_params["labelIds"] = label_ids

            results = self.service.users().messages().list(**query_params).execute()
            messages = results.get("messages", [])

            detailed_messages = []
            for msg in messages:
                msg_detail = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                detailed_messages.append(self._parse_message(msg_detail))

            return detailed_messages
        except HttpError as error:
            logger.error(f"Failed to get inbox messages: {error}")
            return []
        except Exception as error:
            logger.error(f"Error accessing Gmail service: {error}")
            return []

    def _create_auth_flow(self) -> Flow:
        client_config = self.cache.get_config()
        flow = Flow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = client_config["web"]["redirect_uris"][0]
        return flow

    def _read_user_creds(self) -> Optional[Credentials]:
        try:
            data = self.cache.get("creds", None)
            if not data:
                return None

            creds = Credentials.from_authorized_user_info(data, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            return creds
        except Exception as error:
            logger.error(f"Failed to read user credentials: {error}")
            return None

    def _parse_message(self, msg: dict) -> dict:
        """Parse message details"""
        headers = msg["payload"]["headers"]
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "")

        # Get message body
        body = self._get_message_body(msg["payload"])

        return {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "subject": subject,
            "from": sender,
            "date": date,
            "snippet": msg.get("snippet", ""),
            "body": body,
            "labels": msg.get("labelIds", []),
        }

    def _get_message_body(self, payload: dict) -> str:
        """Extract message body from payload"""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    return base64.urlsafe_b64decode(data).decode("utf-8")
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8")
        return ""

    def send_reply(
        self,
        message_id: str,
        thread_id: str,
        reply_text: str,
        to: str,
        subject: str = None,
    ) -> bool:
        """Send a reply to an email"""
        try:
            if not self.service:
                return False

            message = MIMEText(reply_text)
            message["to"] = to
            if subject:
                message["subject"] = subject
            else:
                message["subject"] = "Re: "  # Will be set properly from original

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            self.service.users().messages().send(
                userId="me", body={"raw": raw_message, "threadId": thread_id}
            ).execute()

            # Mark as read
            self.mark_as_read(message_id)

            return True
        except HttpError as error:
            logger.error(f"Error sending reply: {error}")
            return False

    def apply_label(self, message_id: str, label_name: str) -> bool:
        """Apply a label to a message"""
        try:
            if not self.service:
                return False

            labels = self.service.users().labels().list(userId="me").execute()
            label_id = next(
                (l["id"] for l in labels.get("labels", []) if l["name"] == label_name),
                None,
            )

            if not label_id:
                label_id = self._create_label(label_name)

            self.service.users().messages().modify(
                userId="me", id=message_id, body={"addLabelIds": [label_id]}
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Error applying label: {error}")
            return False
        except Exception as error:
            logger.error(f"Error accessing Gmail service: {error}")
            return False

    def _create_label(self, label_name: str) -> str:
        """Create a new label"""
        label = (
            self.service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        return label["id"]

    def archive_message(self, message_id: str) -> bool:
        """Archive a message (remove from inbox)"""
        try:
            if not self.service:
                return False

            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["INBOX"]},
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Error archiving message: {error}")
            return False
        except Exception as error:
            logger.error(f"Error accessing Gmail service: {error}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Error marking as read: {error}")
            return False

    def extract_email(self, email_string: str) -> str:
        """Extract email address from 'Name <email@domain.com>' format"""
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email_string)
        return match.group(0) if match else email_string.lower()
