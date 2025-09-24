import Constants from "expo-constants";

const extra: any = Constants?.expoConfig?.extra ?? {};

export const APP_ENV: string = extra.APP_ENV ?? "dev";
export const API_BASE_URL_MOBILE: string = extra.API_BASE_URL_MOBILE ?? "http://127.0.0.1:8000";
export const API_BASE_URL = API_BASE_URL_MOBILE; // алиас, чтобы импортировать единообразно
