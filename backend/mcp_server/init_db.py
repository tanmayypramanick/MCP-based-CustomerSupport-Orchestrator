import pandas as pd
from sqlalchemy import text
from mcp_server.utils.db import engine, Base, SessionLocal
from mcp_server.models.db_models import CRM

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")

session = SessionLocal()

try:
    crm_df = pd.read_csv("../data/CRM.csv")
    print(f"✅ Loaded CRM.csv with {len(crm_df)} records before cleaning.")

    # Rename columns
    crm_df.rename(columns={
        'Customer Email': 'customer_email',
        'Customer Name': 'customer_name',
        'Customer Age': 'customer_age',
        'Customer Gender': 'customer_gender'
    }, inplace=True)

    # ✅ Remove duplicate emails
    crm_df.drop_duplicates(subset=['customer_email'], inplace=True)
    print(f"✅ After removing duplicates: {len(crm_df)} records.")

    # ✅ Truncate the table
    session.execute(text("TRUNCATE TABLE crm RESTART IDENTITY CASCADE;"))
    session.commit()

    # ✅ Insert row by row
    for _, row in crm_df.iterrows():
        crm_record = CRM(
            customer_email=row['customer_email'],
            customer_name=row['customer_name'],
            customer_age=row['customer_age'],
            customer_gender=row['customer_gender']
        )
        session.add(crm_record)
        session.commit()

    print("✅ CRM data loaded successfully!")

except Exception as e:
    print(f"❌ Error loading CRM data: {e}")

finally:
    session.close()
