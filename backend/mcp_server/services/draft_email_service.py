import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

def generate_email_draft(customer_name, issue_type, product_purchased, jira_id):
    first_name = customer_name.split()[0] if customer_name else "Customer"
    prompt = (
        f"Write a short and professional email reply to a customer named {first_name} who is facing a '{issue_type}' issue "
        f"related to their '{product_purchased}'. Inform them that a support ticket with ID '{jira_id}' has been created "
        "and the team will get back within 24 hours. Use a helpful and courteous tone. Sign the email as 'AI-Orchestrator'."
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        logger.info("✅ Draft email generated successfully.")
        return content.strip()
    except Exception as e:
        logger.exception("❌ Failed to generate email draft")
        return None
