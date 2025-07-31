import pandas as pd
from mcp_server.models.db_models import Ticket
from mcp_server.utils.db import SessionLocal

csv_path = "../data/customer_query.csv"
df = pd.read_csv(csv_path)

session = SessionLocal()
for _, row in df.iterrows():
    email = row["Customer Email"]
    product = row.get("Product Purchased")
    
    ticket = session.query(Ticket).filter_by(customer_email=email).first()
    if ticket and not ticket.product_purchased:
        ticket.product_purchased = product

session.commit()
session.close()
print("✅ Backfilled product_purchased for tickets.")
