"use client";
import ProtectedRoute from "@/routes/ProtectedRoute";
import { getSettings } from "@/services/notificationService";
import { useEffect, useState } from "react";

export default function ModeratorSettingsPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    getSettings().then(setData).catch(() => setData({ email: true, sms: false }));
  }, []);

  return (
    <ProtectedRoute requiredRole="moderator">
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Moderator Settings (stub)</h1>
        <pre className="mt-4 bg-gray-100 p-4 rounded">{JSON.stringify(data, null, 2)}</pre>
      </main>
    </ProtectedRoute>
  );
}
