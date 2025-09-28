"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { confirmEmailCode } from "@/services/authEmailService";

export default function VerifyEmailPage() {
  const params = useSearchParams();
  const email = (params.get("email") || "").toLowerCase();
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(60);
  const router = useRouter();

  useEffect(() => {
    const t = setInterval(() => setCooldown((c) => (c > 0 ? c - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await confirmEmailCode({ email, code });
      if (res.response.ok) {
        router.push("/dashboard");
      } else {
        const data = await res.response.json().catch(() => ({}));
        setError(data?.message ?? "Verification failed");
      }
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <main className="p-8">
      <h1>Verify email</h1>
      <p className="text-gray-600">Email: {email}</p>
      <form onSubmit={onSubmit} className="flex flex-col gap-3 max-w-md">
        <label>
          Code (6 digits)
          <input value={code} onChange={(e) => setCode(e.target.value)} className="border p-2 w-full" />
        </label>
        <button className="border p-2" type="submit">Confirm</button>
        {cooldown > 0 && <p className="text-gray-500">Resend available in {cooldown}s</p>}
        {error && <p className="text-red-600">{error}</p>}
      </form>
    </main>
  );
}
