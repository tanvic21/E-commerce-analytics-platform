import sqlite3

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pipeline_name TEXT,
        run_start_time TEXT,
        run_end_time TEXT,
        status TEXT,
        records_extracted INTEGER,
        records_valid INTEGER,
        records_rejected INTEGER,
        records_inserted INTEGER,
        records_updated INTEGER,
        watermark TEXT
    )
""")

conn.commit()

print("Pipeline runs table created successfully.")

conn.close()