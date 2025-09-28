"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { socialGoogleLogin } from "@/src/services/authSocialService";

export default function GoogleCallback() {
  const router = useRouter();
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code") || undefined;
    const redirect_uri = window.location.origin + "/auth/callback/google";
    if (!code) { router.replace("/"); return; }
    socialGoogleLogin({ code, redirect_uri }).then(() => router.replace("/dashboard")).catch(() => router.replace("/"));
  }, [router]);
  return <p>Signing in…</p>;
}
