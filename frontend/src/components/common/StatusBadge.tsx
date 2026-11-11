import { Badge } from "@/components/ui/badge";

const TONES: Record<string, string> = {
  nuevo: "bg-sky-100 text-sky-800",
  contenido: "bg-emerald-100 text-emerald-800",
  resuelto: "bg-slate-100 text-slate-800",
  falso_positivo: "bg-zinc-100 text-zinc-600",
};

export function StatusBadge({ value }: { value: string }) {
  return <Badge className={TONES[value] ?? ""}>{value}</Badge>;
}
