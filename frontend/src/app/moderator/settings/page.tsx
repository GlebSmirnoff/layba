"use client";
import { useEffect, useState } from "react";
import ProtectedRoute from "@/routes/ProtectedRoute";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://backend.localhost";

export default function ModeratorSettingsPage() {
  const [data, setData] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/notifications/settings/`, { credentials: "include" })
      .then((r) => (r.ok ? r.json() : { email: true, sms: false }))
      .then(setData)
      .catch(() => setData({ email: true, sms: false }));
  }, []);

  async function save() {
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE}/api/notifications/settings/`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data ?? { email: true, sms: false }),
      });
      const j = await r.json();
      setData(j);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ProtectedRoute requiredRole="moderator">
      <main className="p-8 space-y-4">
        <h1 className="text-2xl font-semibold">Moderator Settings (stub)</h1>
        <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(data, null, 2)}</pre>
        <button
          className="rounded-xl px-4 py-2 shadow text-sm border"
          onClick={save}
          disabled={busy}
        >
          {busy ? "Saving..." : "Save"}
        </button>
      </main>
    </ProtectedRoute>
  );
}
