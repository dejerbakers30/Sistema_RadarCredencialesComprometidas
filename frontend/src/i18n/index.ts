import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import es from "./es.json";

i18n.use(initReactI18next).init({
  resources: { es: { translation: es } },
  lng: import.meta.env.VITE_DEFAULT_LOCALE ?? "es",
  fallbackLng: "es",
  interpolation: { escapeValue: false },
});

export default i18n;
