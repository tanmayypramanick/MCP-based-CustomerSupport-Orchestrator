import os
import requests
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()
logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Optional: standard fallback list
STANDARD_ISSUE_CATEGORIES = [
    "Billing", "Technical", "Refund", "Account", "Shipping", "Login", 
    "Feature Request", "Bug Report", "Complaint", "Other"
]

def extract_label(response: str) -> str:
    """Extracts the first valid label from the response based on known issue types."""
    for label in STANDARD_ISSUE_CATEGORIES:
        if label.lower() in response.lower():
            return label
    return "Other"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def classify_issue_llm(ticket_description: str) -> str:
    prompt = (
        "You're a professional support ticket classifier. Given the customer message below, "
        "respond with ONLY the most relevant category label — just one or two words — "
        "from the following industry-standard types:\n"
        "Billing, Technical, Refund, Account, Shipping, Login, Feature Request, Bug Report, Complaint, Other.\n\n"
        f"Customer message:\n{ticket_description}\n\n"
        "Respond ONLY with the best matching label, no explanation, no quotes, no punctuation."
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You classify support queries into clean, standard labels."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    try:
        logger.info("Sending classification request to DeepSeek...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        label = response.json()["choices"][0]["message"]["content"].strip()
        logger.info(f"Raw LLM label: {label}")
        return label.split("\n")[0].strip()  # Just in case multiple lines
    except requests.Timeout:
        logger.error("DeepSeek API timed out")
        return "Other"
    except requests.RequestException as e:
        logger.exception(f"DeepSeek API error: {e}")
        return "Other"
