const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://backend.localhost";

export async function devSessionLogin(email: string, role: "user" | "moderator" = "user") {
  const r = await fetch(`${API_BASE}/auth/session/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role }),
  });
  if (!r.ok) throw new Error(String(r.status));
  // success → редирект на /dashboard
  if (typeof window !== "undefined") window.location.href = "/dashboard";
}
