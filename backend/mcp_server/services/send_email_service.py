import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email: str, subject: str, plain_text: str, html_text: str) -> bool:
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(plain_text)
        msg.add_alternative(html_text, subtype="html")

        logger.info(f"📤 Sending email to {to_email} with subject: {subject}")
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        logger.exception("❌ Failed to send email")
        return False
