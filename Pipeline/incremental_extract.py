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

print(f"Current watermark: {watermark}")

incoming = pd.read_csv(SOURCE_PATH)

incoming["modified_at"] = pd.to_datetime(
    incoming["modified_at"]
)

watermark = pd.to_datetime(watermark)

incremental = incoming[
    incoming["modified_at"] > watermark
].copy()

print(f"Records extracted: {len(incremental)}")

print(
    incremental[
        ["order_id", "order_status", "modified_at"]
    ]
)

conn.close()