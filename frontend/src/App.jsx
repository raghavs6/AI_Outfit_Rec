import { useState, useEffect } from "react";

const BASE = {
  position: "absolute",
  fontFamily: "'Space Grotesk', sans-serif",
};

const pillBtn = {
  borderRadius: 999,
  border: "1.5px solid rgba(255,255,255,0.7)",
  background: "transparent",
  color: "#fff",
  padding: "10px 24px",
  letterSpacing: "0.12em",
  cursor: "pointer",
  fontSize: "0.75rem",
  textTransform: "uppercase",
  display: "flex",
  alignItems: "center",
  gap: 10,
};

const cornerText = {
  fontSize: "0.7rem",
  letterSpacing: "0.18em",
  color: "rgba(255,255,255,0.75)",
  textTransform: "uppercase",
  fontFamily: "'Space Grotesk', sans-serif",
};

export default function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(t);
  }, [toast]);

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
      setToast(data.user_id);
    } catch (err) {
      setError(err.message);
      setToast(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        background:
          "radial-gradient(ellipse at 30% 50%, #1a1f35 0%, #080c18 50%, #000 100%)",
      }}
    >
      {/* Top-left: START NOW */}
      <button
        style={{ ...BASE, ...pillBtn, top: 24, left: 24 }}
        onClick={createGuestUser}
        disabled={loading}
      >
        {loading ? "Loading…" : "Start Now"}
      </button>

      {/* Top-right: MENU */}
      <button style={{ ...BASE, ...pillBtn, top: 24, right: 24 }}>
        <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={{ display: "block", width: 18, height: 1.5, background: "#fff" }} />
          <span style={{ display: "block", width: 18, height: 1.5, background: "#fff" }} />
        </span>
        Menu
      </button>

      {/* Center: star + brand */}
      <div
        style={{
          ...BASE,
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 16,
        }}
      >
        <svg
          width={60}
          height={60}
          viewBox="0 0 60 60"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M 30 0 C 30 14 16 30 0 30 C 14 30 30 44 30 60 C 30 46 44 30 60 30 C 46 30 30 16 30 0 Z"
            fill="white"
          />
        </svg>

        <span
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: "clamp(2.5rem, 6vw, 4.5rem)",
            fontWeight: 700,
            letterSpacing: "0.25em",
            color: "#fff",
            textTransform: "uppercase",
            whiteSpace: "nowrap",
          }}
        >
          FitAI
        </span>
      </div>

      {/* Bottom-left tagline */}
      <span style={{ ...BASE, ...cornerText, bottom: 40, left: 32 }}>
        Style the Ordinary
      </span>

      {/* Bottom-right tagline */}
      <span style={{ ...BASE, ...cornerText, bottom: 40, right: 32 }}>
        Elevate the Everyday
      </span>

      {/* Bottom-center subtitle */}
      <span
        style={{
          ...BASE,
          bottom: 32,
          left: "50%",
          transform: "translateX(-50%)",
          textAlign: "center",
          fontSize: "0.65rem",
          letterSpacing: "0.1em",
          color: "rgba(255,255,255,0.5)",
          textTransform: "uppercase",
          whiteSpace: "nowrap",
          fontFamily: "'Space Grotesk', sans-serif",
        }}
      >
        Your AI Stylist for a Smarter, More Confident Wardrobe
      </span>

      {/* Toast */}
      {toast && (
        <div
          style={{
            ...BASE,
            bottom: 80,
            left: "50%",
            transform: "translateX(-50%)",
            background: "rgba(255,255,255,0.15)",
            backdropFilter: "blur(8px)",
            borderRadius: 999,
            padding: "8px 20px",
            color: "#fff",
            fontSize: "0.7rem",
            letterSpacing: "0.08em",
            whiteSpace: "nowrap",
            border: "1px solid rgba(255,255,255,0.25)",
          }}
        >
          {toast}
        </div>
      )}
    </div>
  );
}
