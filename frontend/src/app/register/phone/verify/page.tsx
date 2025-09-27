"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { getCsrf, verifyPhoneCode } from "@/services/authService";

export default function VerifyPhonePage() {
  const params = useSearchParams();
  const phone = params.get("phone") || "";
  const method = (params.get("method") || "sms") as "sms" | "call";
  const [code, setCode] = useState("");
  const [last4, setLast4] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(60);
  const router = useRouter();

  useEffect(() => {
    const t = setInterval(() => setCooldown((c) => (c > 0 ? c - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, []);

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await getCsrf();
      const body = method === "sms" ? { phone, code } : { phone, last4 };
      const res = await verifyPhoneCode(body as any);
      if (res.response.ok) {
        router.push("/dashboard");
      } else {
        const data = await res.response.json().catch(() => ({}));
        setError(data?.message ?? "Verification failed");
      }
    } catch (err) {
      setError(String(err));
    }
  }, [phone, code, last4, method, router]);

  return (
    <main className="p-8">
      <h1>Verify ({method})</h1>
      <p className="text-gray-600">Phone: {phone}</p>
      <form onSubmit={onSubmit} className="flex flex-col gap-3 max-w-md">
        {method === "sms" ? (
          <label>
            Code (6 digits)
            <input value={code} onChange={(e) => setCode(e.target.value)} className="border p-2 w-full" />
          </label>
        ) : (
          <label>
            Last 4 digits (call)
            <input value={last4} onChange={(e) => setLast4(e.target.value)} className="border p-2 w-full" />
          </label>
        )}

        <button className="border p-2" type="submit">Verify</button>
        {cooldown > 0 && <p className="text-gray-500">Resend available in {cooldown}s</p>}
        {error && <p className="text-red-600">{error}</p>}
      </form>
    </main>
  );
}
