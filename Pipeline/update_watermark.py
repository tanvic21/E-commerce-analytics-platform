import sqlite3
from datetime import datetime

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get records currently in staging
cursor.execute("""
    SELECT COUNT(*)
    FROM orders_staging
""")

records_processed = cursor.fetchone()[0]

# Only update the watermark when records were processed
if records_processed > 0:

    cursor.execute("""
        SELECT MAX(modified_at)
        FROM orders_staging
    """)

    new_watermark = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE pipeline_control
        SET
            last_successful_watermark = ?,
            last_run_time = ?,
            status = 'SUCCESS',
            records_processed = ?
        WHERE pipeline_name = 'orders_pipeline'
    """, (
        new_watermark,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        records_processed
    ))

else:

    cursor.execute("""
        UPDATE pipeline_control
        SET
            last_run_time = ?,
            status = 'SUCCESS',
            records_processed = 0
        WHERE pipeline_name = 'orders_pipeline'
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))

conn.commit()

cursor.execute("""
    SELECT *
    FROM pipeline_control
    WHERE pipeline_name = 'orders_pipeline'
""")

print(cursor.fetchone())

conn.close()