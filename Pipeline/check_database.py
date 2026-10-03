import sqlite3

DB_PATH = r"..\\database\\ecommerce.db"

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM orders")
count = cursor.fetchone()[0]

print(f"Orders in database: {count}")

cursor.execute("SELECT * FROM orders LIMIT 5")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()