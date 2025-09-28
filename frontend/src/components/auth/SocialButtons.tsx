"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { socialFacebookLogin } from "@/src/services/authSocialService";

export default function SocialButtons() {
  const router = useRouter();

  async function devGoogle() {
    // dev: шлём «id_token» напрямую (работает при DEV_SOCIAL_MOCK=1)
    const res = await fetch("http://localhost:8000/auth/social/google", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: "dev-google-id-token" }),
    });
    if (res.ok) router.push("/dashboard");
  }

  async function devApple() {
    const res = await fetch("http://localhost:8000/auth/social/apple", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: "dev-apple-id-token" }),
    });
    if (res.ok) router.push("/dashboard");
  }

  async function devFacebook() {
    await socialFacebookLogin({ access_token: "dev-facebook-token" });
    router.push("/dashboard");
  }

  return (
    <div className="flex gap-2">
      <button onClick={devGoogle}>Sign in with Google (dev)</button>
      <button onClick={devFacebook}>Sign in with Facebook (dev)</button>
      <button onClick={devApple}>Sign in with Apple (dev)</button>
    </div>
  );
}
