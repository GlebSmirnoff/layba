"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { socialAppleLogin } from "@/src/services/authSocialService";

export default function AppleCallback() {
  const router = useRouter();
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id_token = params.get("id_token") || undefined;
    if (!id_token) { router.replace("/"); return; }
    socialAppleLogin({ id_token }).then(() => router.replace("/dashboard")).catch(() => router.replace("/"));
  }, [router]);
  return <p>Signing in…</p>;
}
