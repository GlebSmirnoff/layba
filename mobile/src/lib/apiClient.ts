import { API_BASE_URL } from "../config/env";

function joinUrl(base: string, path: string) {
  if (!base.endsWith("/")) base += "/";
  if (path.startsWith("/")) path = path.slice(1);
  return base + path;
}

export type ApiResponse<T = any> = { data: T; headers: Headers };

export async function apiGet<T = any>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const url = joinUrl(API_BASE_URL, path);
  const res = await fetch(url, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const data = (await res.json().catch(() => null)) as T;
  if (!res.ok) {
    const msg = typeof (data as any)?.message === "string" ? (data as any).message : `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return { data, headers: res.headers };
}
