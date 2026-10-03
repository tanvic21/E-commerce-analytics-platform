import sqlite3

DB_PATH = r"..\database\ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT
        order_id,
        customer_id,
        order_status,
        payment_method,
        shipping_city,
        shipping_state,
        modified_at
    FROM orders
    WHERE order_id IN ('O005001', 'O020001', 'O020002')
    ORDER BY order_id
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()