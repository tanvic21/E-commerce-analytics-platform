import sqlite3
import pandas as pd
import sys

DB_PATH = r"..\database\ecommerce.db"

if len(sys.argv) < 2:
    print("Error: Source file not provided.")
    sys.exit(1)

SOURCE_PATH = rf".\source\{sys.argv[1]}"

conn = sqlite3.connect(DB_PATH)

watermark = pd.read_sql_query(
    """
    SELECT last_successful_watermark
    FROM pipeline_control
    WHERE pipeline_name = 'orders_pipeline'
    """,
    conn
).iloc[0, 0]

watermark = pd.to_datetime(watermark)

incoming = pd.read_csv(SOURCE_PATH)

incoming["modified_at"] = pd.to_datetime(
    incoming["modified_at"]
)

incremental = incoming[
    incoming["modified_at"] > watermark
].copy()

incremental.to_sql(
    "orders_staging",
    conn,
    if_exists="replace",
    index=False
)

print(f"Records loaded into staging: {len(incremental)}")

conn.close()