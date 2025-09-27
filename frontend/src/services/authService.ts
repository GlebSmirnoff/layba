import { api } from "@/shared/api/client"; // сгенерированный клиент (шаг 2)
import { NEXT_PUBLIC_API_BASE_URL } from "@/shared/config"; // если есть; иначе можно убрать

type SendCodeBody = { phone: string; method: "sms" | "call" };
type VerifyBody = { phone: string; code?: string; last4?: string };

export async function getCsrf() {
  await api.GET("/auth/csrf/", { credentials: "include" });
}

export async function sendPhoneCode(body: SendCodeBody) {
  return api.POST("/auth/phone/send_code", {
    body,
    credentials: "include",
  });
}

export async function verifyPhoneCode(body: VerifyBody) {
  return api.POST("/auth/phone/verify", {
    body,
    credentials: "include",
  });
}
