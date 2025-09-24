"use client";
import { useEffect, useState } from "react";
import { api } from "@/api/client";

export default function HealthzPage() {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    api.get("healthz").json<any>().then(setData).catch(e => setErr(String(e)));
  }, []);

  return (
    <main style={{ padding: 24 }}>
      <h1>Backend /healthz</h1>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
      {err && <pre style={{ color: "crimson" }}>{err}</pre>}
    </main>
  );
}
