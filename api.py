from fastapi import FastAPI
from pydantic import BaseModel
import re
import requests
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

# =============================
# ✅ App
# =============================
app = FastAPI(title="VocaStock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# ✅ Database
# =============================
DB_PATH = "stock.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# =============================
# ✅ NLP Normalization (Arabic + English)
# =============================
def normalize_question(q: str) -> str:
    q = q.strip().lower()

    # ✅ توحيد الحروف العربية
    arabic_map = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
    }
    for k, v in arabic_map.items():
        q = q.replace(k, v)

    q = re.sub(r"[ًٌٍَُِّْـ]", "", q)

    # ✅ مرادفات الفئات
    category_map = {
        "موبايل": "phone",
        "هاتف": "phone",
        "جوال": "phone",
        "phone": "phone",
        "smartphone": "phone",

        "لاب": "laptop",
        "كمبيوتر": "laptop",
        "حاسب": "laptop",
        "notebook": "laptop",

        "ساعه": "watch",
        "ساعه ذكيه": "watch",
        "watch": "watch",

        "سماعه": "audio",
        "سماعات": "audio",
        "airpods": "audio",
        "headphones": "audio",
    }

    for k, v in category_map.items():
        q = q.replace(k, v)

    # ✅ مرادفات المنتجات
    product_map = {
        "ايفون": "iphone",
        "آيفون": "iphone",
        "iphone": "iphone",

        "سامسونج": "samsung",
        "جلاكسي": "galaxy",

        "ايربودز": "airpods",
        "اير بودز": "airpods",

        "باوربانك": "powerbank",
        "باور بنك": "powerbank",
    }

    for k, v in product_map.items():
        q = q.replace(k, v)

    # ✅ توحيد أسماء العملاء (سارة = sara = sarah)
    name_map = {
        "ساره": "sara",
        "سارة": "sara",
        "sara": "sara",
        "sarah": "sara",

        "احمد": "ahmed",
        "أحمد": "ahmed",
        "ahmed": "ahmed",
    }

    for k, v in name_map.items():
        q = q.replace(k, v)

    # ✅ تحويل الأرقام المنطوقة
    number_map = {
        "واحد": "1", "واحدة": "1", "one": "1",
        "اثنين": "2", "اتنين": "2", "two": "2",
        "ثلاثه": "3", "تلاته": "3", "three": "3",
        "اربعه": "4", "اربعة": "4", "four": "4",
        "خمسه": "5", "خمسة": "5", "five": "5",
        "سته": "6", "ستة": "6", "six": "6",
        "سبعه": "7", "سبعة": "7", "seven": "7",
        "ثمانيه": "8", "ثمانية": "8", "eight": "8",
        "تسعه": "9", "تسعة": "9", "nine": "9",
        "عشره": "10", "عشرة": "10", "ten": "10",
    }

    for k, v in number_map.items():
        q = q.replace(k, v)

    return q

# =============================
# ✅ Schema Extraction
# =============================
def get_schema_description():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    schema = ""
    for t in tables:
        table = t[0]
        cur.execute(f"PRAGMA table_info({table});")
        cols = cur.fetchall()
        schema += f"Table {table}:\n"
        for c in cols:
            schema += f"  - {c[1]} {c[2]}\n"
        schema += "\n"

    conn.close()
    return schema

# =============================
# ✅ Ollama Configuration
# =============================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def build_prompt(user_question: str) -> str:
    schema = get_schema_description()

    return f"""
You are an expert SQLite Text-to-SQL assistant.

IMPORTANT RULES:
- Use only simple SELECT queries.
- NEVER generate invalid SQL.
- Use LIKE for string comparisons.
- For out of stock words (out of stock, نفدت, خلص):
  quantity_in_stock = 0
- For available stock:
  quantity_in_stock > 0
- Do NOT use subqueries unless necessary.
- Return ONLY SQL without explanations.

Database schema:
{schema}

User question:
{user_question}

SQL:
""".strip()

def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if "response" not in data:
        raise RuntimeError("Invalid Ollama response")

    text = data["response"].strip()
    text = re.sub(r"```sql", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    match = re.search(r"select\s.+", text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Model did not return SQL")

    return match.group().strip()

# =============================
# ✅ SQL Execution
# =============================
def execute_sql(sql: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    conn.close()
    return cols, rows

# =============================
# ✅ API Schema
# =============================
class Question(BaseModel):
    question: str

# =============================
# ✅ API Endpoint
# =============================
@app.post("/ask")
def ask_vocastock(q: Question):
    try:
        normalized_q = normalize_question(q.question)

        prompt = build_prompt(normalized_q)
        sql = call_ollama(prompt)
        cols, rows = execute_sql(sql)

        return {
            "question": q.question,
            "normalized_question": normalized_q,
            "sql": sql,
            "columns": cols,
            "rows": rows,
        }

    except Exception as e:
        return {"error": str(e)}
