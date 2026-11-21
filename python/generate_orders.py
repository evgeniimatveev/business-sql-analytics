import os
from dotenv import load_dotenv

load_dotenv()  # reads DB_PASSWORD from .env (see .env.example)

import psycopg2
import psycopg2.extras
import pandas as pd
from faker import Faker
import random
from tqdm import tqdm

# Database connection settings
DB_NAME = "business_analysis"
DB_USER = "postgres"
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = "localhost"
DB_PORT = "5432"

# Initialize Faker
fake = Faker()

# ✅ Ensure valid order statuses match DB constraint (fix spelling if needed)
VALID_STATUSES = {"pending", "shipped", "delivered", "cancelled"}  # Must match DB CHECK constraint

# Function to generate synthetic order data
def generate_orders(n=5000):
    """Generates synthetic orders data"""
    orders = []
    for _ in tqdm(range(n), desc="Generating Orders"):
        customer_id = random.randint(1, 5000)  # Random customer ID
        order_date = fake.date_time_between(start_date="-1y", end_date="now")  # Order date
        status = random.choice(list(VALID_STATUSES))  # Ensure only valid status
        total_amount = round(random.uniform(5.0, 500.0), 2)  # Random total amount

        orders.append((customer_id, order_date, status, total_amount))
    
    return pd.DataFrame(orders, columns=["customer_id", "order_date", "status", "total_amount"])

# Function to insert data into PostgreSQL
def insert_data(conn, df, table_name, columns):
    """Inserts data into PostgreSQL table"""
    try:
        cur = conn.cursor()
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
        tuples = [tuple(x) for x in df.to_numpy()]
        psycopg2.extras.execute_values(cur, sql, tuples)
        conn.commit()
        cur.close()
        print(f"✅ Inserted {len(df)} rows into {table_name}")
    except Exception as e:
        print(f"❌ Error inserting into {table_name}: {e}")

# Full process to generate and insert orders
def generate_and_insert_orders():
    """Connects to PostgreSQL, generates order data, and inserts into the database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        print("✅ Connected to PostgreSQL")

        df_orders = generate_orders(5000)

        # ✅ Debug: Print any invalid statuses before inserting
        invalid_statuses = set(df_orders["status"]) - VALID_STATUSES
        if invalid_statuses:
            print(f"❌ ERROR! Invalid statuses detected: {invalid_statuses}")
            print("🔍 Fix your VALID_STATUSES or check the DB constraint.")
            return  

        insert_data(conn, df_orders, "orders", ["customer_id", "order_date", "status", "total_amount"])

        conn.close()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

# Run script
if __name__ == "__main__":
    generate_and_insert_orders()