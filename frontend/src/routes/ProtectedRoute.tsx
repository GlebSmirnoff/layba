"use client";

import { useEffect, useState, PropsWithChildren } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://backend.localhost";

type Props = PropsWithChildren<{ requiredRole?: "user" | "moderator" }>;

export default function ProtectedRoute({ children, requiredRole }: Props) {
  const [state, setState] = useState<"loading" | "ok" | "forbidden">("loading");
  const router = useRouter();

  useEffect(() => {
    let off = false;
    fetch(`${API_BASE}/profile/me`, { credentials: "include" })
      .then(async (r) => {
        if (r.status !== 200) throw new Error(String(r.status));
        const user = await r.json();
        if (requiredRole && user.role !== requiredRole) {
          if (!off) setState("forbidden");
          return;
        }
        if (!off) setState("ok");
      })
      .catch(() => {
        if (!off) router.replace("/"); // гость -> на главную/логин
      });
    return () => { off = true; };
  }, [router, requiredRole]);

  if (state === "loading") return <div className="p-6 text-sm">Loading…</div>;
  if (state === "forbidden") return <div className="p-6">403 — Forbidden</div>;
  return <>{children}</>;
}
