# stock_text_to_sql.py
import sqlite3
import re

DB_PATH = "stock.db"

def escape_like(value: str) -> str:
    return value.replace("'", "''")

def has_any(q, words):
    return any(w in q for w in words)

def generate_sql_from_nl(nl: str) -> str:
    q_original = nl.strip()
    q = q_original.lower()

    arabic_name_map = {
        "أحمد": "Ahmed Ali",
        "احمد": "Ahmed Ali",
        "سارة": "Sara Hassan",
        "سارا": "Sara Hassan",
        "عمر":  "Omar Yousef",
    }

    # ===============================
    # 1) LIST ALL PRODUCTS
    # ===============================
    if has_any(q, ["product", "products", "منتج", "منتجات", "مخزون"]) and \
       has_any(q, ["list", "all", "show", "كل", "اعرض"]):
        return """
        SELECT id, name, category, price, quantity_in_stock
        FROM products
        ORDER BY id
        """

    # ===============================
    # 2) OUT OF STOCK PRODUCTS ✅ FIXED
    # ===============================
    if has_any(q, ["out of stock", "zero stock", "no stock", "خلصت", "نفدت", "مش موجود", "خلص"]):
        return """
        SELECT id, name, category, price, quantity_in_stock
        FROM products
        WHERE quantity_in_stock = 0
        ORDER BY id
        """

    # ===============================
    # 3) LOW STOCK
    # ===============================
    m_en = re.search(r"stock\s+less\s+than\s+(\d+)", q)
    m_ar = re.search(r"اقل من\s+(\d+)", q)

    if has_any(q, ["low stock", "قليل", "قليلة", "هتخلص"]) or m_en or m_ar:
        if m_en:
            threshold = int(m_en.group(1))
        elif m_ar:
            threshold = int(m_ar.group(1))
        else:
            threshold = 5
        return f"""
        SELECT id, name, category, price, quantity_in_stock
        FROM products
        WHERE quantity_in_stock < {threshold}
        ORDER BY quantity_in_stock ASC
        """

    # ===============================
    # 4) ✅ TOP SELLING PRODUCTS (NEW)
    # ===============================
    if has_any(q, ["top", "best", "best selling", "most sold", "الاكثر", "الاكثر مبيع", "الأعلى مبيع"]):
        m = re.search(r"top\s*(\d+)", q)
        limit = int(m.group(1)) if m else 5

        return f"""
        SELECT 
            products.name,
            SUM(order_items.quantity) AS total_sold
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        GROUP BY products.name
        ORDER BY total_sold DESC
        LIMIT {limit}
        """

    # ===============================
    # 5) LIST ALL ORDERS
    # ===============================
    if has_any(q, ["order", "orders", "اوردر", "طلب", "طلبات"]) and \
       has_any(q, ["list", "all", "show", "كل", "اعرض"]):
        return """
        SELECT 
            orders.id AS order_id,
            customers.name AS customer,
            orders.order_date,
            orders.total_amount
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        ORDER BY orders.order_date
        """

    # ===============================
    # 6) ORDERS FOR SPECIFIC CUSTOMER
    # ===============================
    customer_name = None

    m_cust_en = re.search(r"customer\s+([a-zA-Z ]+)", q_original, re.IGNORECASE)
    if m_cust_en:
        customer_name = m_cust_en.group(1).strip()

    for ar, en in arabic_name_map.items():
        if ar in q_original:
            customer_name = en
            break

    if customer_name and has_any(q, ["order", "orders", "طلب", "اوردر"]):
        name_like = escape_like(customer_name)
        return f"""
        SELECT 
            orders.id AS order_id,
            customers.name AS customer,
            orders.order_date,
            orders.total_amount
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        WHERE customers.name LIKE '%{name_like}%'
        ORDER BY orders.order_date
        """

    # ===============================
    # 7) TOTAL SALES
    # ===============================
    if has_any(q, ["total sales", "total revenue", "اجمالي المبيعات", "مجموع المبيعات"]):
        return """
        SELECT SUM(total_amount) AS total_sales
        FROM orders
        """

    # ===============================
    # 8) LIST CUSTOMERS
    # ===============================
    if has_any(q, ["customer", "customers", "عميل", "عملاء"]) and \
       has_any(q, ["list", "all", "show", "كل", "اعرض"]):
        return """
        SELECT id, name, city
        FROM customers
        ORDER BY id
        """

    # ===============================
    # FALLBACK
    # ===============================
    raise ValueError("❌ Could not understand the query. Try a simpler sentence.")

def execute_sql(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    conn.close()
    return cols, rows
# ===========================
# ✅ CONSOLE TEST MODE
# ===========================
if __name__ == "__main__":
    print("🎙️ VocaStock Console Mode")
    print("Type your question in English or Arabic.")
    print("Type 'exit' to quit.")

    while True:
        q = input("\nAsk VocaStock: ").strip()

        if q.lower() in ("exit", "quit"):
            print("👋 Exiting VocaStock...")
            break

        try:
            sql = generate_sql_from_nl(q)
            print("\nSQL:\n", sql.strip())

            cols, rows = execute_sql(sql)

            print("\nResult:")
            print(cols)
            for r in rows:
                print(r)

        except Exception as e:
            print("Error:", e)

