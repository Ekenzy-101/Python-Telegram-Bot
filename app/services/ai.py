from datetime import datetime
import json
import re
from openai import OpenAI
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered email assistant using Claude"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_url,
        )

    def analyze_email(self, email_content: dict) -> dict:
        """Analyze email and extract intent"""
        prompt = f"""Analyze this email and provide:
1. Category (urgent/follow-up/spam/invoice/general)
2. Sentiment (positive/neutral/negative)
3. Key topics (comma-separated)
4. Suggested action

Email:
From: {email_content['from']}
Subject: {email_content['subject']}
Body: {email_content['body'][:500]}

Respond in JSON format."""

        try:
            completion = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = completion.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {}

    def generate_reply(self, email_content: dict, template: dict) -> str:
        """Generate reply based on template"""
        template_text = template["content"]

        # Extract email details
        from_field = email_content["from"]
        sender_name = from_field.split("<")[0].strip().strip('"')
        sender_email = self._extract_email(from_field)

        # Analyze email to extract more variables
        analysis = self.analyze_email(email_content)
        topics = analysis.get("key_topics", "")
        category = analysis.get("category", "general")

        # Extract company from email domain
        company = (
            sender_email.split("@")[1].split(".")[0].capitalize()
            if "@" in sender_email
            else ""
        )

        # Determine next step based on category
        next_step = self._determine_next_step(category, analysis)

        # Replace variables
        variables = {
            "sender_name": sender_name,
            "sender_email": sender_email,
            "subject": email_content["subject"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "company": company,
            "topic": topics.split(",")[0].strip() if topics else "your message",
            "topics": topics,
            "next_step": next_step,
            "category": category,
        }

        for key, value in variables.items():
            template_text = template_text.replace(f"{{{key}}}", str(value))

        # Use AI to personalize
        prompt = f"""Create a professional email reply based on this template and context.
Make it natural and personalized. Use the template as a guide but adapt it to the specific email.

Template: {template_text}

Original Email:
From: {email_content['from']}
Subject: {email_content['subject']}
Body: {email_content['body'][:500]}

Email Analysis:
Category: {category}
Topics: {topics}
Suggested Action: {analysis.get('suggested_action', '')}

Generate only the reply text, no preamble. Make it sound natural and contextually appropriate."""

        try:
            completion = self.client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Reply generation error: {e}")
            return template_text

    def _extract_email(self, email_string: str) -> str:
        """Extract email address from string"""
        import re

        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", email_string)
        return match.group(0) if match else email_string.lower()

    def _determine_next_step(self, category: str, analysis: dict) -> str:
        """Determine next step based on email category"""
        if category == "urgent":
            return "I will prioritize this and respond as soon as possible"
        elif category == "follow-up":
            return "I will follow up on this matter"
        elif category == "invoice":
            return "I will process this invoice accordingly"
        else:
            return "I will review this and get back to you"
