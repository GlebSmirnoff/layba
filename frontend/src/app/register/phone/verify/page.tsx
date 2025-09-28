'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useMemo, useState } from 'react';
import { api } from '@/api/client';

export default function VerifyPhonePage() {
  const router = useRouter();
  const sp = useSearchParams();
  const phone = sp.get('phone') ?? '';
  const method = (sp.get('method') ?? 'sms') as 'sms' | 'call';

  const isSms = method === 'sms';
  const [code, setCode] = useState('');
  const [last4, setLast4] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const label = useMemo(() => (isSms ? 'Код из SMS' : 'Последние 4 цифры входящего номера'), [isSms]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const body = isSms ? { phone, code } : { phone, last4 };
      const { data, error } = await api.POST('/auth/phone/verify', { body });

      if (error) {
        setErr(error.data?.message ?? 'Не удалось подтвердить телефон');
        return;
      }

      // успешная сессия — на /dashboard
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Verify phone</h1>
      <p>Телефон: {phone}</p>
      <form onSubmit={onSubmit}>
        <div>
          <label>{label}: </label>
          <input
            value={isSms ? code : last4}
            onChange={(e) => (isSms ? setCode(e.target.value) : setLast4(e.target.value))}
            placeholder={isSms ? '123456' : '1234'}
          />
        </div>
        <button disabled={loading} style={{ marginTop: 12 }}>
          {loading ? 'Проверяю...' : 'Подтвердить'}
        </button>
        {err && <p style={{ color: 'crimson' }}>{err}</p>}
      </form>
    </main>
  );
}
