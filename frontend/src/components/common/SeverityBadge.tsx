import { Badge } from "@/components/ui/badge";

const TONES: Record<string, string> = {
  baja: "bg-emerald-100 text-emerald-800",
  media: "bg-amber-100 text-amber-800",
  alta: "bg-orange-100 text-orange-800",
  critica: "bg-rose-100 text-rose-800",
};

export function SeverityBadge({ value }: { value: string }) {
  return <Badge className={TONES[value] ?? ""}>{value}</Badge>;
}
