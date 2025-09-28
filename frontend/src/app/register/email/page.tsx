"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { sendEmailCode } from "@/services/authEmailService";

export default function RegisterEmailPage() {
  const [email, setEmail] = useState("test@example.com");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await sendEmailCode({ email });
      if (res.response.ok) {
        router.push(`/register/email/verify?email=${encodeURIComponent(email.toLowerCase())}`);
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
      <h1>Email confirm</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-3 max-w-md">
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} className="border p-2 w-full" />
        </label>
        <button className="border p-2" type="submit">Send code</button>
        {error && <p className="text-red-600">{error}</p>}
      </form>
    </main>
  );
}
