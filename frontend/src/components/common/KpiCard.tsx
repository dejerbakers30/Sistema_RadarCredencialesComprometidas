import { cn } from "@/lib/utils";

type Tone = "default" | "warning" | "success" | "info" | "danger";

const tones: Record<Tone, string> = {
  default: "border-border",
  warning: "border-amber-400 bg-amber-50",
  success: "border-emerald-400 bg-emerald-50",
  info: "border-sky-400 bg-sky-50",
  danger: "border-rose-400 bg-rose-50",
};

export function KpiCard({
  title, value, tone = "default",
}: { title: string; value: string | number; tone?: Tone }) {
  return (
    <div className={cn("rounded-lg border p-4", tones[tone])}>
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}
