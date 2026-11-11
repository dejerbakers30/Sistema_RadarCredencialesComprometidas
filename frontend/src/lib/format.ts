// format.ts
import { format, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatDateTime(iso: string) {
  try {
    return format(parseISO(iso), "dd/MM/yyyy HH:mm", { locale: es });
  } catch {
    return iso;
  }
}
