import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(
    customer_name: str,
    customer_email: str,
    issue_type: str,
    jira_id: str,
    ticket_id: int,
    ticket_description: str,
    product_purchased: str = "the product"
) -> bool:
    # Replace placeholder with actual product
    description = ticket_description.replace("{product_purchased}", product_purchased)

    message = (
        f":rotating_light: *New Support Ticket Created*\n\n"
        f"*Customer:* {customer_name}  \n"
        f"*Email:* `{customer_email}`  \n"
        f"*Issue Type:* `{issue_type}`  \n"
        f"*Product:* `{product_purchased}`  \n"
        f"*Ticket ID:* `{ticket_id}`  \n"
        f"*Jira Ticket:* <https://ai-customer-support.atlassian.net/browse/{jira_id}|{jira_id}>\n\n"
        f"*Description:*\n{description}\n\n"
        f"Please review and take appropriate action."
    )

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)

    if response.status_code != 200:
        print(f"❌ Slack Error: {response.status_code} - {response.text}")
    return response.status_code == 200
