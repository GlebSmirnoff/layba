"use client";
import ProtectedRoute from "@/routes/ProtectedRoute";

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <main className="p-8">
        <h1 className="text-2xl font-semibold">Dashboard (stub)</h1>
        <p className="mt-2 text-sm opacity-70">Вы авторизованы. Дальше прикрутим формы входа.</p>
      </main>
    </ProtectedRoute>
  );
}
