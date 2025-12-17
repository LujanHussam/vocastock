This guide explains exactly how to run both backend (FastAPI) and frontend (React + Vite) on any laptop.

⚠️ 1. Required Installations
✔ Install Python 3.10+

Download from: https://www.python.org/downloads/

Make sure to check:
☑ Add Python to PATH

✔ Install Node.js (LTS version)

Download from: https://nodejs.org/

This will install:

node

npm

📁 2. Project Structure (What you will receive)

When you unzip the VocaStock folder, you should find:

VocaStock/
│
├── api.py
├── create_stock_db.py
├── stock.db
├── stock_text_to_sql.py
├── ai_text_to_sql.py
├── vocastock_app.py
│
└── vocastock-ui/
    ├── public/
    ├── src/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js

🚀 3. How to Run the Backend (FastAPI)
Step 1 — Open a Terminal inside the main project folder

Example:

cd VocaStock

Step 2 — Install required Python packages
pip install fastapi uvicorn requests

Step 3 — Make sure stock.db exists

If you want to recreate it:

python create_stock_db.py

Step 4 — Run FastAPI server
uvicorn api:app --reload


Backend should now be running at:

👉 http://127.0.0.1:8000

💻 4. How to Run the Frontend (React + Vite)
Step 1 — Open a second terminal

Navigate to the UI folder:

cd VocaStock/vocastock-ui

Step 2 — Install node_modules (VERY IMPORTANT)

This command automatically creates node_modules:

npm install

Step 3 — Run the frontend dev server
npm run dev


You will get a local URL such as:

👉 http://localhost:5173

Open it in the browser — the VocaStock UI will appear.

🎤 5. Voice Mode Notes

English button forces EN recognition

Arabic button forces AR recognition

Both work instantly with backend

Make sure Chrome is used for microphone support

🧠 6. For Text-to-SQL (Ollama)

Each teammate must install Ollama locally:

Download: https://ollama.com/download

Then pull the model:

ollama pull qwen2.5:1.5b


Run the server:

ollama run qwen2.5:1.5b


🟦 أولاً: تشغيل الـ Backend
1 — افتح Terminal

وروّح على مجلد المشروع الأساسي:

cd C:\Users\GEEK\Desktop\VocaStock  (غيروه للpath بتاعكم)

2 — شغّل الـ backend:
uvicorn api:app --reload


لو كله تمام هتلاقي رسالة زي كده:

Uvicorn running on http://127.0.0.1:8000


معنى كده إن الـ backend شغّال ومظبوط.

🟩 ثانياً: تشغيل الـ Frontend

لازم تفتح Terminal جديد (مش نفس اللي فيه backend)

1 — روّح لمجلد الواجهة:
cd C:\Users\GEEK\Desktop\VocaStock\vocastock-ui

2 — شغّل الواجهة:
npm run dev


لو اشتغل صح هتشوف:

VITE ready at http://localhost:5173


افتح الرابط ده في المتصفح 👌
وده الموقع اللي فيه الصوت والـ AI Text-to-SQL
