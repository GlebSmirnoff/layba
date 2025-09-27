"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { getCsrf, sendPhoneCode } from "@/services/authService";

export default function RegisterPhonePage() {
  const [phone, setPhone] = useState("+380000000000");
  const [method, setMethod] = useState<"sms" | "call">("sms");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await getCsrf();
      const res = await sendPhoneCode({ phone, method });
      if (res.response.ok) {
        router.push(`/register/phone/verify?phone=${encodeURIComponent(phone)}&method=${method}`);
      } else {
        const data = await res.response.json().catch(() => ({}));
        setError(data?.message ?? "Failed to send code");
      }
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <main className="p-8">
      <h1>Phone login</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-3 max-w-md">
        <label>
          Phone (E.164)
          <input value={phone} onChange={(e) => setPhone(e.target.value)} className="border p-2 w-full" />
        </label>

        <label>
          Method
          <select value={method} onChange={(e) => setMethod(e.target.value as any)} className="border p-2 w-full">
            <option value="sms">SMS (6 digits)</option>
            <option value="call">Call (last 4)</option>
          </select>
        </label>

        <button className="border p-2" type="submit">Send</button>
        {error && <p className="text-red-600">{error}</p>}
      </form>
    </main>
  );
}
