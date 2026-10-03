import sqlite3

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    DROP TABLE IF EXISTS pipeline_run_counts
""")

cursor.execute("""
    CREATE TABLE pipeline_run_counts (
        run_id INTEGER PRIMARY KEY,
        records_inserted INTEGER,
        records_updated INTEGER
    )
""")

conn.commit()

print("pipeline_run_counts table recreated successfully.")

conn.close()