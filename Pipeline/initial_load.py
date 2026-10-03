import sqlite3
import pandas as pd

CSV_PATH = "../data/orders_clean.csv"
DB_PATH = "../database/ecommerce.db"

# Read CSV
orders = pd.read_csv(r"C:\\Users\\LENOVO\\Desktop\\BI Projects\\E-Commerce Analytics Platform\\clean data\\orders_clean.csv" )
# Connect to SQLite 
conn = sqlite3.connect(r"..\database\ecommerce.db")

# Load into SQLite
orders.to_sql(
    "orders",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print(f"Initial load completed: {len(orders)} records")