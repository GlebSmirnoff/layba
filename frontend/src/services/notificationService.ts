const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://backend.localhost";

export async function getSettings() {
  try {
    const r = await fetch(`${API_BASE}/api/notifications/settings/`, { credentials: "include" });
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  } catch {
    // dev stub fallback
    return { email: true, sms: false };
  }
}

export async function updateSettings(payload: any) {
  try {
    const r = await fetch(`${API_BASE}/api/notifications/settings/`, {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  } catch {
    return payload;
  }
}
