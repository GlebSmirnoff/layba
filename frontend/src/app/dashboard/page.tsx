'use client';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <main style={{ padding: 24 }}>
        <h1>Dashboard (stub)</h1>
        <p>Вы авторизованы. Дальше прикрутим формы входа.</p>
      </main>
    </ProtectedRoute>
  );
}
