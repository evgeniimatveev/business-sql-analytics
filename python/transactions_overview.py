import os
from dotenv import load_dotenv

load_dotenv()  # reads DB_PASSWORD from .env (see .env.example)

import pandas as pd
import psycopg2
import os

print("🚀 Script started...")  # Checking if the script runs

# Connect to PostgreSQL
try:
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(
        dbname="business_analysis",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
        host="localhost",
        port="5432"
    )
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# SQL Query: Transactions overview
query = """
SELECT 
    transaction_id, 
    order_id, 
    amount, 
    payment_method, 
    transaction_date
FROM transactions
ORDER BY transaction_date DESC;
"""

try:
    print("🔄 Running SQL query...")
    df = pd.read_sql(query, conn)
    print(f"✅ SQL query executed! DataFrame shape: {df.shape}")

    if df.empty:
        print("⚠️ Warning: The query returned an empty DataFrame!")

    # Ensure the 'excel' directory exists
    excel_dir = os.path.abspath("excel")  

    if not os.path.exists(excel_dir):
        print(f"⚠️ Warning: Directory does not exist! Creating: {excel_dir}")
        os.makedirs(excel_dir)

    # Set the Excel file path
    excel_path = os.path.join(excel_dir, "transactions_overview.xlsx")
    print(f"💾 Saving file to: {excel_path}")

    # Save to Excel
    df.to_excel(excel_path, index=False, engine="openpyxl")
    print(f"📊 Transactions overview saved successfully at: {excel_path}!")

except Exception as e:
    print(f"❌ Error executing SQL or saving Excel: {e}")

finally:
    conn.close()
    print("🔒 Connection closed.")