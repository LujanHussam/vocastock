# create_stock_db.py
import sqlite3

DB_PATH = "stock.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# Create tables (if missing)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    quantity_in_stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# =========================
# Seed sample data (once)
# =========================
def table_empty(table_name: str) -> bool:
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0] == 0

if table_empty("products"):
    products = [
        (1, "iPhone 15",          "Phones",      42000.0, 12),
        (2, "Samsung S24",        "Phones",      38000.0, 5),
        (3, "AirPods Pro",        "Accessories",  9000.0, 2),
        (4, "Dell G15 Laptop",    "Laptops",     65000.0, 7),
        (5, "Anker 20k Powerbank","Accessories", 1500.0, 0),
        (6, "Apple Watch",        "Wearables",   15000.0, 3),
    ]
    cursor.executemany(
        "INSERT INTO products (id, name, category, price, quantity_in_stock) VALUES (?, ?, ?, ?, ?)",
        products
    )

if table_empty("customers"):
    customers = [
        (1, "Ahmed Ali",    "Cairo"),
        (2, "Sara Hassan",  "Giza"),
        (3, "Omar Yousef",  "Alexandria"),
    ]
    cursor.executemany(
        "INSERT INTO customers (id, name, city) VALUES (?, ?, ?)",
        customers
    )

if table_empty("orders"):
    orders = [
        (1, 1, "2025-12-01", 45000.0),
        (2, 2, "2025-12-02",  9000.0),
        (3, 1, "2025-12-03", 65000.0),
        (4, 3, "2025-12-05", 19500.0),
    ]
    cursor.executemany(
        "INSERT INTO orders (id, customer_id, order_date, total_amount) VALUES (?, ?, ?, ?)",
        orders
    )

if table_empty("order_items"):
    order_items = [
        (1, 1, 1, 1, 42000.0),  # order 1: iPhone 15
        (2, 1, 5, 2, 1500.0),   # order 1: 2x powerbank
        (3, 2, 3, 1, 9000.0),   # order 2: AirPods
        (4, 3, 4, 1, 65000.0),  # order 3: Dell G15
        (5, 4, 2, 1, 38000.0),  # order 4: Samsung S24
        (6, 4, 6, 1, 15000.0),  # order 4: Apple Watch
    ]
    cursor.executemany(
        "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
        order_items
    )

conn.commit()
conn.close()
print("✅ stock.db created / updated successfully.")
