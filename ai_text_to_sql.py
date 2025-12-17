# ai_text_to_sql.py
import sqlite3
from pathlib import Path
import re
import requests

print("✅ ai_text_to_sql.py started successfully")

# ======================================
# 📂 Database Configuration
# ======================================
DB_PATH = "stock.db"

def get_connection():
    db_file = Path(DB_PATH)
    if not db_file.exists():
        raise FileNotFoundError(f"{DB_PATH} not found in project folder.")
    return sqlite3.connect(DB_PATH)

def get_schema_description():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]

    lines = []
    for table in tables:
        if table.startswith("sqlite_"):
            continue
        lines.append(f"Table {table}:")
        cur.execute(f"PRAGMA table_info({table});")
        cols = cur.fetchall()
        for _, name, col_type, _, _, pk in cols:
            pk_str = " PRIMARY KEY" if pk else ""
            lines.append(f"  - {name} {col_type}{pk_str}")
        lines.append("")

    conn.close()
    return "\n".join(lines)

# ======================================
# 🔧 Ollama Configuration
# ======================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


# ======================================
# 🧠 Prompt Builder
# ======================================
def build_prompt(user_question: str) -> str:
    schema = get_schema_description()

    examples = """
Examples of questions and good SQL (SQLite):

Q: "list all products"
SQL: SELECT id, name, category, price, quantity_in_stock
     FROM products
     ORDER BY id;

Q: "show products that are out of stock"
SQL: SELECT id, name, category, price, quantity_in_stock
     FROM products
     WHERE quantity_in_stock = 0
     ORDER BY id;

Q: "top 5 best selling products"
SQL: SELECT
        products.name,
        SUM(order_items.quantity) AS total_sold
     FROM order_items
     JOIN products ON order_items.product_id = products.id
     GROUP BY products.name
     ORDER BY total_sold DESC
     LIMIT 5;

Q: "orders for customer Ahmed Ali"
SQL: SELECT
        orders.id AS order_id,
        customers.name AS customer,
        orders.order_date,
        orders.total_amount
     FROM orders
     JOIN customers ON orders.customer_id = customers.id
     WHERE customers.name LIKE '%Ahmed Ali%'
     ORDER BY orders.order_date;

Q: "إجمالي المبيعات"
SQL: SELECT SUM(total_amount) AS total_sales
     FROM orders;

Q: "ايه اكتر منتج اتباع؟"
SQL: SELECT
        products.name,
        SUM(order_items.quantity) AS total_sold
     FROM order_items
     JOIN products ON order_items.product_id = products.id
     GROUP BY products.name
     ORDER BY total_sold DESC
     LIMIT 1;
"""

    prompt = f"""
You are an expert Text-to-SQL assistant for a stock management system.
Return ONLY a valid SQLite SELECT query. No explanation. No comments.

Database Schema:
{schema}

The user can speak English or Arabic (including Egyptian Arabic).

{examples}

User Question:
"{user_question}"

Return ONLY the SQL query.
"""
    return prompt.strip()

# ======================================
# 🧠 Call Ollama
# ======================================
def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if "response" not in data:
        raise RuntimeError("Invalid Ollama response format")

    text = data["response"].strip()

    # تنظيف أي fences
    text = re.sub(r"```sql", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    # التقاط أول SELECT فقط
    match = re.search(r"select\s", text, flags=re.IGNORECASE)
    if match:
        sql = text[match.start():].strip()
    else:
        sql = text

    return sql


# ======================================
# 🔎 Execute SQL
# ======================================
def execute_sql(sql: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    return cols, rows

# ======================================
# 🎙️ Console Mode
# ======================================
def main():
    print("🎙️ VocaStock AI Mode")
    print("Ask about products, stock, orders, customers in English or Arabic.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask VocaStock: ").strip()
        if question.lower() in ("exit", "quit"):
            break

        if not question:
            continue

        try:
            prompt = build_prompt(question)
            sql = call_ollama(prompt)

            print("\nSQL:\n", sql)
            cols, rows = execute_sql(sql)

            print("\nResult:")
            print(cols)
            if rows:
                for r in rows:
                    print(r)
            else:
                print("(no rows)")

        except Exception as e:
            print("❌ Error:", e)

        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    main()
