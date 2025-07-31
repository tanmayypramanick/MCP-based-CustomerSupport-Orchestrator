import os
import requests
import logging
from dotenv import load_dotenv
from pathlib import Path
import json

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Load .env
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Read environment variables
JIRA_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "CUS")

def create_jira_ticket(description: str, issue_type: str, ticket_id: int, product: str, customer_email: str = "N/A") -> str:
    if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
        logger.error("❌ Missing one or more Jira environment variables!")
        return "JIRA-CONFIG-ERROR"

    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)

    summary = f"[{issue_type}] Issue with {product} - Ticket #{ticket_id}"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": f"Customer Email: {customer_email}\n"},
                            {"type": "text", "text": f"Issue Type: {issue_type}\n"},
                            {"type": "text", "text": f"Product: {product}\n"},
                            {"type": "text", "text": f"Ticket ID: {ticket_id}\n\n"},
                            {"type": "text", "text": f"Description:\n{description}"}
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"},
            "labels": ["automated", "customer-support"]
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    logger.debug("📦 Payload being sent to Jira:")
    logger.debug(json.dumps(payload, indent=2))

    try:
        response = requests.post(
            url,
            auth=auth,
            json=payload,
            headers=headers,
            timeout=10
        )

        logger.debug(f"📬 Jira Response Status: {response.status_code}")
        logger.debug(f"📬 Jira Response Text: {response.text}")

        if response.status_code == 201:
            ticket_key = response.json().get("key", "JIRA-UNKNOWN")
            logger.info(f"✅ Jira ticket created: {ticket_key}")
            return ticket_key
        else:
            logger.error(f"❌ Jira creation failed: {response.status_code} - {response.text}")
            return f"JIRA-ERROR-{response.status_code}"

    except requests.RequestException as e:
        logger.exception("❌ Jira API Request failed")
        return f"JIRA-EXCEPTION: {str(e)}"
