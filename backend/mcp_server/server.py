import sys
import os
import logging
import pandas as pd
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.DEBUG)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(override=True)

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

CSV_PATH = os.getenv("CUSTOMER_QUERY_CSV", "../data/customer_query.csv")

from mcp_server.utils.db import SessionLocal
from mcp_server.models.db_models import CRM, Ticket
from mcp_server.services.llm_service import classify_issue_llm
from mcp_server.services.jira_service import create_jira_ticket
from mcp_server.services.slack_service import send_slack_message
from mcp_server.services.draft_email_service import generate_email_draft
from mcp_server.services.send_email_service import send_email

mcp = FastMCP("AI-Customer-Support-Orchestrator")


@mcp.tool()
def process_query(customer_email: str, ticket_description: str, product_purchased: str = "Unknown") -> dict:
    db = SessionLocal()
    try:
        crm_record = db.query(CRM).filter(CRM.customer_email == customer_email).first()
        customer_name = crm_record.customer_name if crm_record else "Guest"

        new_ticket = Ticket(
            customer_email=customer_email,
            ticket_description=ticket_description,
            product_purchased=product_purchased,
            status="Open"
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        return {
            "ticket_id": new_ticket.ticket_id,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "status": new_ticket.status
        }
    except Exception as e:
        logger.exception("Error in process_query")
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
def classify_issue(ticket_id: int) -> dict:
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}

        logger.info(f"Classifying issue for ticket {ticket_id}: {ticket.ticket_description}")
        issue_type = classify_issue_llm(ticket.ticket_description)
        logger.info(f"Issue classified as {issue_type} for ticket {ticket_id}")
        ticket.issue_type = issue_type
        db.commit()
        db.refresh(ticket)

        return {"ticket_id": ticket_id, "issue_type": issue_type}
    except Exception as e:
        logger.exception("Error in classify_issue")
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
def create_jira(ticket_id: int) -> dict:
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}

        # Replace placeholder with actual product
        product = ticket.product_purchased or "the product"
        description = ticket.ticket_description.replace("{product_purchased}", product)

        # Call the Jira service with correct argument names
        jira_id = create_jira_ticket(
            description=description,
            issue_type=ticket.issue_type or "Unclassified",
            ticket_id=ticket.ticket_id,
            product=product,
            customer_email=ticket.customer_email,
        )

        # Store Jira ID in the ticket record
        ticket.jira_id = jira_id
        db.commit()

        return {"ticket_id": ticket.ticket_id, "jira_id": jira_id}

    except Exception as e:
        logger.exception("Error in create_jira")
        return {"error": str(e)}
    finally:
        db.close()
        
@mcp.tool()
def notify_slack(ticket_id: int) -> dict:
    db = SessionLocal()
    try:
        # Fetch ticket and customer
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}

        customer = db.query(CRM).filter(CRM.customer_email == ticket.customer_email).first()
        customer_name = customer.customer_name if customer else "Unknown"

        # Replace placeholder with actual product
        product = ticket.product_purchased or "the product"
        description = ticket.ticket_description.replace("{product_purchased}", product)

        # Send Slack notification
        success = send_slack_message(
            customer_name=customer_name,
            customer_email=ticket.customer_email,
            issue_type=ticket.issue_type or "Unclassified",
            jira_id=ticket.jira_id or "N/A",
            ticket_id=ticket.ticket_id,
            ticket_description=description,
            product_purchased=product
        )

        if success:
            ticket.slack_sent = True
            db.commit()
            return {"ticket_id": ticket_id, "slack_sent": True}
        else:
            return {"ticket_id": ticket_id, "slack_sent": False, "error": "Failed to send message"}

    except Exception as e:
        logger.exception("Error in notify_slack")
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
def draft_email(ticket_id: int) -> dict:
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            return {"error": "Ticket not found"}

        customer = db.query(CRM).filter(CRM.customer_email == ticket.customer_email).first()
        customer_name = customer.customer_name if customer else "Customer"
        issue_type = ticket.issue_type or "technical"
        product = ticket.product_purchased or "the product"
        jira_id = ticket.jira_id or "CUS-XXXX"

        email_body = generate_email_draft(customer_name, issue_type, product, jira_id)
        if email_body:
            ticket.email_draft = email_body
            db.commit()
            return {"ticket_id": ticket_id, "draft_email": email_body}
        else:
            return {"error": "Failed to generate email draft"}
    except Exception as e:
        logger.exception("Error in draft_email")
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
def send_email_tool(ticket_id: int) -> dict:
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        if not ticket:
            logger.error(f"❌ Ticket not found for ID: {ticket_id}")
            return {"error": "Ticket not found"}

        customer = db.query(CRM).filter(CRM.customer_email == ticket.customer_email).first()
        first_name = (customer.customer_name or "Customer").split()[0] if customer else "Customer"
        issue_type = ticket.issue_type or "Support"
        product = ticket.product_purchased or "your product"
        jira_id = ticket.jira_id or "N/A"

        subject = f"{issue_type} Issue with {product}"

        plain_text = f"""Hi {first_name},

Thank you for reaching out regarding the {issue_type} issue with your {product}. We've created a support ticket with the ID {jira_id} for easy tracking.

Our team is reviewing your concern and will get back to you within 24 hours. We appreciate your patience and apologize for any inconvenience.

If you have any additional details to share, feel free to reply to this email.

Best regards,  
AI-Orchestrator
"""

        html_text = f"""
<html>
  <body>
    <p>Hi <strong>{first_name}</strong>,</p>

    <p>
      Thank you for reaching out regarding the <strong>{issue_type}</strong> issue with your 
      <strong>{product}</strong>. We've created a support ticket with the ID 
      <strong>{jira_id}</strong> for easy tracking.
    </p>

    <p>
      Our team is reviewing your concern and will get back to you within <strong>24 hours</strong>. 
      We appreciate your patience and apologize for any inconvenience.
    </p>

    <p>If you have any additional details to share, feel free to reply to this email.</p>

    <p>Best regards,<br><strong>AI-Orchestrator</strong></p>
  </body>
</html>
"""

        sent = send_email(ticket.customer_email, subject, plain_text, html_text)

        if sent:
            ticket.email_sent = True
            db.commit()
            logger.info(f"✅ Email sent successfully for ticket {ticket_id}")
            return {"ticket_id": ticket_id, "email_sent": True}
        else:
            logger.error(f"❌ Email failed for ticket {ticket_id}")
            return {"ticket_id": ticket_id, "email_sent": False, "error": "Failed to send email"}

    except Exception as e:
        logger.exception("🔥 Exception in send_email_tool")
        return {"error": str(e)}
    finally:
        db.close()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
@mcp.tool()
def run_batch_pipeline(num_queries: int = 1) -> dict:
    try:
        df = pd.read_csv(CSV_PATH)
        chosen = df.sample(n=num_queries).to_dict(orient="records")
        results = []

        for entry in chosen:
            customer_email = entry.get("customer_email")
            ticket_description = entry.get("ticket_description", "No description provided")
            product_purchased = entry.get("product_purchased", "Unknown")

            logger.info(f"🔹 Starting pipeline for {customer_email}")

            ticket_info = process_query(customer_email, ticket_description, product_purchased)
            logger.info(f"🪪 Ticket created: {ticket_info}")

            ticket_id = ticket_info.get("ticket_id")
            if not ticket_id:
                logger.error(f"❌ Ticket creation failed for {customer_email}")
                results.append({"error": "Ticket creation failed", "email": customer_email})
                continue

            classification = classify_issue(ticket_id)
            logger.info(f"🧠 Classification done: {classification}")

            jira = create_jira(ticket_id)
            logger.info(f"📌 Jira created: {jira}")

            slack = notify_slack(ticket_id)
            logger.info(f"💬 Slack notification sent: {slack}")

            draft = draft_email(ticket_id)
            logger.info(f"📄 Email drafted: {draft}")

            email = send_email_tool(ticket_id)
            logger.info(f"📧 Email sent: {email}")

            results.append({
                "email": customer_email,
                "ticket_id": ticket_id,
                "classification": classification,
                "jira": jira,
                "slack": slack,
                "email": email
            })

        logger.info("✅ Batch pipeline complete.")
        return {"processed": results}

    except Exception as e:
        logger.exception("🔥 Batch pipeline failed")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("Starting MCP FastMCP server...")
    mcp.run(transport="streamable-http")