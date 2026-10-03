import sqlite3

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM orders_staging
""")

deleted_rows = cursor.rowcount

conn.commit()

print(f"Staging cleanup completed: {deleted_rows} records removed.")

conn.close()