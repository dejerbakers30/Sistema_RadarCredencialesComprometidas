import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

type Tone = "default" | "warning" | "success" | "info" | "danger";

const tones: Record<Tone, string> = {
  default: "border-border",
  warning: "border-amber-400 bg-amber-50",
  success: "border-emerald-400 bg-emerald-50",
  info: "border-sky-400 bg-sky-50",
  danger: "border-rose-400 bg-rose-50",
};

export function KpiCard({
  title, value, tone = "default", icon: Icon, helper,
}: { title: string; value: string | number; tone?: Tone; icon?: LucideIcon; helper?: string }) {
  return (
    <div className={cn("rounded-xl border bg-white p-5 shadow-sm", tones[tone])}>
      <div className="flex items-start justify-between gap-3"><div className="text-sm font-medium text-slate-500">{title}</div>{Icon && <div className="rounded-lg bg-slate-100 p-2 text-slate-500"><Icon className="h-4 w-4" /></div>}</div>
      <div className="mt-3 text-2xl font-bold tracking-tight text-slate-950">{value}</div>
      {helper && <div className="mt-1 text-xs text-slate-500">{helper}</div>}
    </div>
  );
}
