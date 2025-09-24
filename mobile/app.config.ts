import { ConfigContext, ExpoConfig } from "@expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "LaybaMobile",
  slug: "layba-mobile",
  scheme: "layba",
  version: "0.1.0",
  extra: {
    // Меняй под цель теста: iOS симулятор — 127.0.0.1, Android эмулятор — 10.0.2.2, физ. устройство — IP ПК
    API_BASE_URL_MOBILE: process.env.API_BASE_URL_MOBILE ?? "http://127.0.0.1:8000",
    APP_ENV: process.env.APP_ENV ?? "dev",
  },
});
