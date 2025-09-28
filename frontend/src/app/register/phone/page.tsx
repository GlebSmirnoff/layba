'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { api } from '@/api/client';

export default function RegisterPhonePage() {
  const router = useRouter();
  const [phone, setPhone] = useState('+380000000000');
  const [method, setMethod] = useState<'sms' | 'call'>('sms');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      // получаем CSRF (если нужно для DRF)
      await api.GET('/auth/csrf/');

      const { error } = await api.POST('/auth/phone/send_code', {
        body: { phone, method },
      });
      if (error) {
        // error уже типизирован из схемы
        setErr(error.data?.message ?? 'Не удалось отправить код');
        return;
      }

      // переходим на ввод кода
      const q = new URLSearchParams({ phone, method });
      router.push(`/register/phone/verify?${q}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Phone registration</h1>
      <form onSubmit={onSubmit}>
        <div>
          <label>Phone (E.164): </label>
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+380..."
          />
        </div>

        <div style={{ marginTop: 8 }}>
          <label>
            <input
              type="radio"
              checked={method === 'sms'}
              onChange={() => setMethod('sms')}
            />
            SMS
          </label>
          <label style={{ marginLeft: 12 }}>
            <input
              type="radio"
              checked={method === 'call'}
              onChange={() => setMethod('call')}
            />
            Call (last4)
          </label>
        </div>

        <button disabled={loading} style={{ marginTop: 12 }}>
          {loading ? 'Отправляю...' : 'Отправить код'}
        </button>

        {err && <p style={{ color: 'crimson' }}>{err}</p>}
      </form>
    </main>
  );
}
