import sqlite3
import sys
import pandas as pd
from datetime import datetime

DB_PATH = r"..\database\ecommerce.db"
if len(sys.argv) < 2:
    print("Error: run_id not provided.")
    sys.exit(1)

run_id = int(sys.argv[1])
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table to store the latest upsert counts
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_run_counts (
        run_time TEXT,
        records_inserted INTEGER,
        records_updated INTEGER
    )
""")

# Read staging data
staging = pd.read_sql_query(
    "SELECT * FROM orders_staging",
    conn
)

# Validate customer IDs
valid_customers = pd.read_csv(
    r"..\clean data\customers_clean.csv"
)

valid_customer_ids = set(
    valid_customers["customer_id"]
)

staging = staging[
    staging["customer_id"].isin(valid_customer_ids)
].copy()

inserted = 0
updated = 0

# Process each record
for _, row in staging.iterrows():

    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE order_id = ?",
        (row["order_id"],)
    )

    exists = cursor.fetchone()[0]

    if exists == 0:

        cursor.execute("""
            INSERT INTO orders (
                order_id,
                customer_id,
                order_date,
                order_status,
                payment_method,
                shipping_city,
                shipping_state,
                modified_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["order_id"],
            row["customer_id"],
            row["order_date"],
            row["order_status"],
            row["payment_method"],
            row["shipping_city"],
            row["shipping_state"],
            row["modified_at"]
        ))

        inserted += 1

    else:

        cursor.execute("""
            UPDATE orders
            SET
                customer_id = ?,
                order_date = ?,
                order_status = ?,
                payment_method = ?,
                shipping_city = ?,
                shipping_state = ?,
                modified_at = ?
            WHERE order_id = ?
        """, (
            row["customer_id"],
            row["order_date"],
            row["order_status"],
            row["payment_method"],
            row["shipping_city"],
            row["shipping_state"],
            row["modified_at"],
            row["order_id"]
        ))

        updated += 1


# Save counts
cursor.execute("""
    INSERT INTO pipeline_run_counts (
        run_id,
        records_inserted,
        records_updated
    )
    VALUES (?, ?, ?)
""", (
    run_id,
    inserted,
    updated
))

conn.commit()

print(f"Inserted: {inserted}")
print(f"Updated: {updated}")

conn.close()