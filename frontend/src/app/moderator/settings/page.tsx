"use client";
import { useEffect, useState } from "react";
import ProtectedRoute from "@/routes/ProtectedRoute";

import { getSettings, updateSettings, type NotificationSettings } from "@/services/notificationService";

export default function ModeratorSettingsPage() {
  const [data, setData] = useState<NotificationSettings | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getSettings().then(setData).catch(() => setData({ email: true, sms: false }));
  }, []);

  async function save() {
    setBusy(true);
    try {
      if (!data) return;
      const saved = await updateSettings(data);
      setData(saved);
    } finally {
      setBusy(false);
    }
  }

  return (
    <ProtectedRoute requiredRole="moderator">
      <main className="p-8 space-y-4">
        <h1 className="text-2xl font-semibold">Moderator Settings (stub)</h1>
        <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(data ?? { email: true, sms: false }, null, 2)}</pre>
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
