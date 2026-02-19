import { useState } from "react";

const styles = {
  container: {
    fontFamily: "sans-serif",
    maxWidth: 480,
    margin: "80px auto",
    padding: "0 16px",
    textAlign: "center",
  },
  button: {
    padding: "10px 24px",
    fontSize: 16,
    cursor: "pointer",
    borderRadius: 6,
    border: "none",
    background: "#4f46e5",
    color: "#fff",
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: "not-allowed",
  },
  result: {
    marginTop: 24,
    padding: 16,
    background: "#f3f4f6",
    borderRadius: 8,
    textAlign: "left",
    wordBreak: "break-all",
  },
  error: {
    marginTop: 24,
    padding: 16,
    background: "#fee2e2",
    borderRadius: 8,
    color: "#991b1b",
  },
};

export default function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function createGuestUser() {
    setLoading(true);
    setError(null);
    setUser(null);
    try {
      const res = await fetch("/api/v1/users/guest", { method: "POST" });
      if (!res.ok) {
        const body = await res.text();
        throw new Error(`${res.status} ${res.statusText}: ${body}`);
      }
      const data = await res.json();
      setUser(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <h1>AI Outfit Rec</h1>
      <button
        style={{ ...styles.button, ...(loading ? styles.buttonDisabled : {}) }}
        onClick={createGuestUser}
        disabled={loading}
      >
        {loading ? "Creating…" : "Create Guest User"}
      </button>

      {user && (
        <div style={styles.result}>
          <strong>user_id:</strong> {user.user_id}
          <br />
          <strong>created_at:</strong> {user.created_at}
        </div>
      )}

      {error && <div style={styles.error}>Error: {error}</div>}
    </div>
  );
}
