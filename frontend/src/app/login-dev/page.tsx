"use client";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function api(path: string, body?: any) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return r.ok;
}

export default function DevLoginPage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Dev Login</h1>
      <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
        <button onClick={async () => {
          await api("/auth/session/login", { email: "user@example.com", role: "user" });
          location.href = "/dashboard";
        }}>Login as USER</button>

        <button onClick={async () => {
          await api("/auth/session/login", { email: "mod@example.com", role: "moderator" });
          location.href = "/moderator/settings";
        }}>Login as MODERATOR</button>

        <button onClick={async () => {
          await api("/auth/session/logout");
          alert("Logged out");
        }}>Logout</button>
      </div>
    </main>
  );
}
