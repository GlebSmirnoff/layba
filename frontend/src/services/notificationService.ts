/* eslint-disable @typescript-eslint/no-explicit-any */
import { OpenAPI } from "@/shared/api/core/OpenAPI";
import { request as __request } from "@/shared/api/core/request";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://backend.localhost";
OpenAPI.BASE = API_BASE;
OpenAPI.WITH_CREDENTIALS = true;

export type NotificationSettings = { email: boolean; sms: boolean };

export async function getSettings(): Promise<NotificationSettings> {
  const res = await __request(OpenAPI, { method: "GET", url: "/api/notifications/settings/" });
  return res as NotificationSettings;
}

export async function updateSettings(payload: NotificationSettings): Promise<NotificationSettings> {
  const res = await __request(OpenAPI, {
    method: "PUT",
    url: "/api/notifications/settings/",
    body: payload,
    mediaType: "application/json",
  });
  return res as NotificationSettings;
}
