import sqlite3

DB_PATH = r"..\\database\\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_control (
        pipeline_name TEXT PRIMARY KEY,
        last_successful_watermark TEXT,
        last_run_time TEXT,
        status TEXT,
        records_processed INTEGER
    )
""")

cursor.execute("""
    INSERT OR IGNORE INTO pipeline_control (
        pipeline_name,
        last_successful_watermark,
        last_run_time,
        status,
        records_processed
    )
    VALUES (
        'orders_pipeline',
        '2026-09-30 23:59:59',
        NULL,
        'INITIALIZED',
        0
    )
""")

conn.commit()

print("Pipeline control table created.")

cursor.execute("SELECT * FROM pipeline_control")

for row in cursor.fetchall():
    print(row)

conn.close()