'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/api/client';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data, response } = await api.GET('/profile/me', { credentials: 'include' });
        if (!cancelled) setOk(response.ok && !!data);
      } catch {
        if (!cancelled) setOk(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (ok === false) router.replace('/register/phone');
  }, [ok, router]);

  if (ok === null) return <div style={{ padding: 24 }}>Проверка сессии…</div>;
  if (ok === false) return null;
  return <>{children}</>;
}
