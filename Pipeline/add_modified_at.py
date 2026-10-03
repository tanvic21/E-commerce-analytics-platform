import sqlite3

DB_PATH = r"..\\database\\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add modified_at column
cursor.execute("""
    ALTER TABLE orders
    ADD COLUMN modified_at TEXT
""")

# Give existing historical records a baseline timestamp
cursor.execute("""
    UPDATE orders
    SET modified_at = '2026-09-30 23:59:59'
    WHERE modified_at IS NULL
""")

conn.commit()

print("modified_at column added successfully.")

# Verify
cursor.execute("""
    SELECT order_id, modified_at
    FROM orders
    LIMIT 5
""")

for row in cursor.fetchall():
    print(row)

conn.close()