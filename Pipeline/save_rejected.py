import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)

# Read staging
staging = pd.read_sql_query(
    "SELECT * FROM orders_staging",
    conn
)

customers = pd.read_csv(
    r"..\clean data\customers_clean.csv"
)

valid_customers = set(customers["customer_id"])

valid_statuses = {
    "Delivered",
    "Cancelled",
    "Returned",
    "Processing"
}

valid_payment_methods = {
    "UPI",
    "Credit Card",
    "Debit Card",
    "COD",
    "Net Banking"
}

rejected = []

for _, row in staging.iterrows():

    reason = None

    if pd.isna(row["order_id"]):
        reason = "Missing order_id"

    elif row["customer_id"] not in valid_customers:
        reason = "Invalid customer_id"

    elif row["order_status"] not in valid_statuses:
        reason = "Invalid order_status"

    elif row["payment_method"] not in valid_payment_methods:
        reason = "Invalid payment_method"

    elif pd.isna(row["order_date"]):
        reason = "Missing order_date"

    elif pd.isna(row["modified_at"]):
        reason = "Missing modified_at"

    if reason:
        rejected.append({
            "order_id": row["order_id"],
            "rejection_reason": reason,
            "rejected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

rejected_df = pd.DataFrame(rejected)

if not rejected_df.empty:
    rejected_df.to_sql(
        "rejected_orders",
        conn,
        if_exists="append",
        index=False
    )

print(f"Rejected records saved: {len(rejected_df)}")

conn.close()