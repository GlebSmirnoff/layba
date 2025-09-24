import React, { createContext, useContext, useMemo, useState, PropsWithChildren } from "react";
import en from "./en.json";
import uk from "./uk.json";
import pl from "./pl.json";

type Locale = "en" | "uk" | "pl";
const DICTS: Record<Locale, Record<string, string>> = { en, uk, pl } as any;

function translate(dict: Record<string, string>, key: string) {
  return dict[key] ?? key;
}

type I18nCtx = { locale: Locale; setLocale: (l: Locale) => void; t: (key: string) => string };
const I18nContext = createContext<I18nCtx | null>(null);

export const I18nProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const [locale, setLocale] = useState<Locale>("en");
  const dict = DICTS[locale] ?? DICTS.en;
  const value = useMemo(() => ({ locale, setLocale, t: (k: string) => translate(dict, k) }), [locale, dict]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("I18nProvider is missing");
  return ctx;
}
