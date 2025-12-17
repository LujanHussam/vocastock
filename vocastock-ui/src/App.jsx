import { useState, useRef } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [sql, setSql] = useState("");
  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  // 🎙️ حالات الصوت
  const [voiceText, setVoiceText] = useState("");
  const [voiceStatus, setVoiceStatus] = useState("idle"); 
  // idle | listening | captured | error

  // 🌍 وضع اللغة
  const [langMode, setLangMode] = useState("en"); // en | ar

  const recognitionRef = useRef(null);

  // ================================
  // ✅ إرسال السؤال للـ Backend
  // ================================
  const askVocaStock = async (qFromVoice = null) => {
    const finalQuestion = qFromVoice ?? question;
    if (!finalQuestion.trim()) return;

    setLoading(true);
    setError("");
    setSql("");
    setColumns([]);
    setRows([]);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: finalQuestion }),
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setSql(data.sql);
        setColumns(data.columns);
        setRows(data.rows);
      }
    } catch (err) {
      setError("❌ Backend not reachable. Is FastAPI running?");
    }

    setLoading(false);
  };

  // ================================
  // ✅ تشغيل الميكروفون
  // ================================
  const startVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognition = new SpeechRecognition();

    // ✅ تحديد اللغة بدقة حسب الوضع
    recognition.lang = langMode === "ar" ? "ar-EG" : "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognitionRef.current = recognition;

    setVoiceStatus("listening");
    setVoiceText("");
    setError("");
    console.log("🎙️ Listening started in:", recognition.lang);

    recognition.start();

    // ✅ عند التقاط الصوت فعليًا
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;

      console.log("✅ Voice Captured:", transcript);

      setQuestion(transcript);
      setVoiceText(transcript);
      setVoiceStatus("captured");

      // تنفيذ تلقائي بعد التقاط الصوت
      setTimeout(() => {
        askVocaStock(transcript);
      }, 400);
    };

    // ✅ عند حدوث خطأ
    recognition.onerror = (e) => {
      console.error("❌ Speech error:", e);
      setVoiceStatus("error");
    };

    // ✅ عند إيقاف التسجيل
    recognition.onend = () => {
      console.log("🎤 Listening ended");
    };
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>🎙️ VocaStock</h1>
      <p style={styles.subtitle}>
        Ask about stock, orders, customers (English + عربي)
      </p>

      {/* ✅ اختيار اللغة */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
        <button
          onClick={() => setLangMode("en")}
          style={{
            padding: "8px 16px",
            borderRadius: "8px",
            border: langMode === "en" ? "2px solid #22c55e" : "1px solid #444",
            background: langMode === "en" ? "#16a34a" : "#1e293b",
            color: "white",
            cursor: "pointer",
          }}
        >
          🇺🇸 English
        </button>

        <button
          onClick={() => setLangMode("ar")}
          style={{
            padding: "8px 16px",
            borderRadius: "8px",
            border: langMode === "ar" ? "2px solid #22c55e" : "1px solid #444",
            background: langMode === "ar" ? "#16a34a" : "#1e293b",
            color: "white",
            cursor: "pointer",
          }}
        >
          🇪🇬 عربي
        </button>
      </div>

      <div style={styles.box}>
        <input
          style={styles.input}
          placeholder="Ask VocaStock or speak 🎙️"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && askVocaStock()}
        />

        <button
          style={{
            ...styles.micButton,
            background:
              voiceStatus === "listening"
                ? "#dc2626"
                : voiceStatus === "captured"
                ? "#22c55e"
                : "#2563eb",
          }}
          onClick={startVoiceInput}
        >
          {voiceStatus === "listening"
            ? "🎙️ Recording..."
            : voiceStatus === "captured"
            ? "✅ Captured"
            : langMode === "ar"
            ? "🎤 عربي"
            : "🎤 EN"}
        </button>

        <button style={styles.button} onClick={() => askVocaStock()}>
          Ask
        </button>
      </div>

      {/* ✅ مؤشرات حالة الصوت */}
      {voiceStatus === "listening" && (
        <p style={{ color: "#facc15", marginTop: "10px" }}>
          🎙️ Listening... please speak now
        </p>
      )}

      {voiceStatus === "captured" && (
        <p style={{ color: "#22c55e", marginTop: "10px" }}>
          ✅ Voice captured: "{voiceText}"
        </p>
      )}

      {voiceStatus === "error" && (
        <p style={{ color: "#ef4444", marginTop: "10px" }}>
          ❌ Microphone error. Try again
        </p>
      )}

      {loading && <p>⏳ Thinking...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {sql && (
        <div style={styles.card}>
          <h3>Generated SQL</h3>
          <pre>{sql}</pre>
        </div>
      )}

      {rows.length > 0 && (
        <div style={styles.card}>
          <h3>Result</h3>
          <table style={styles.table}>
            <thead>
              <tr>
                {columns.map((c) => (
                  <th key={c} style={styles.th}>
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  {r.map((cell, j) => (
                    <td key={j} style={styles.td}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  page: {
  minHeight: "100vh",
  width: "100vw",
  background: "radial-gradient(circle at top, #020617, #0f172a 60%, #020617)",
  color: "white",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "flex-start",
  padding: "40px 20px",
  fontFamily: "sans-serif",
  overflowX: "hidden",
  },

  title: { fontSize: "48px", marginBottom: "10px" },
  subtitle: { opacity: 0.8, marginBottom: "30px" },
  box: { display: "flex", gap: "10px", marginBottom: "20px" },
  input: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    fontSize: "16px",
  },
  button: {
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    background: "#22c55e",
    fontSize: "16px",
    cursor: "pointer",
  },
  card: {
    background: "#1e293b",
    padding: "20px",
    marginTop: "20px",
    borderRadius: "12px",
  },
  table: { width: "100%", borderCollapse: "collapse" },
  th: { borderBottom: "1px solid #444", padding: "8px" },
  td: { borderBottom: "1px solid #333", padding: "8px" },
  micButton: {
    padding: "12px 18px",
    borderRadius: "8px",
    border: "none",
    color: "white",
    fontSize: "18px",
    cursor: "pointer",
  },
};

export default App;
