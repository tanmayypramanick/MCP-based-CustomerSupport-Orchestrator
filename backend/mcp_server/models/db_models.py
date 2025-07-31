from sqlalchemy import Column, String, Integer, Text, Boolean
from mcp_server.utils.db import Base

class CRM(Base):
    __tablename__ = "crm"
    customer_email = Column(String, primary_key=True)
    customer_name = Column(String)
    customer_age = Column(Integer)
    customer_gender = Column(String)

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_email = Column(String)
    issue_type = Column(String, nullable=True)
    ticket_description = Column(Text)
    product_purchased = Column(String, nullable=True)
    email_draft = Column(Text, nullable=True)
    status = Column(String, default="Open")
    jira_id = Column(String, nullable=True)
    email_sent = Column(Boolean, default=False)
    slack_sent = Column(Boolean, default=False)

