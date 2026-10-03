import sqlite3
import pandas as pd

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)

# Read staging data
staging = pd.read_sql_query(
    "SELECT * FROM orders_staging",
    conn
)

# Read valid customer IDs
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

valid_rows = []
rejected_rows = []

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
        rejected_rows.append({
            "order_id": row["order_id"],
            "rejection_reason": reason
        })
    else:
        valid_rows.append(row.to_dict())

valid = pd.DataFrame(valid_rows)
rejected = pd.DataFrame(rejected_rows)

print(f"Valid records: {len(valid)}")
print(f"Rejected records: {len(rejected)}")

if not rejected.empty:
    print("\nRejected records:")
    print(rejected)

conn.close()