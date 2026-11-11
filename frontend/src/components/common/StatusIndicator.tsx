import { CheckCircle2, Clock3, CircleAlert, RotateCcw, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const statuses: Record<string, { label: string; className: string; icon: React.ElementType }> = {
  exitoso: { label: "Exitosa", className: "bg-emerald-50 text-emerald-700 ring-emerald-200", icon: CheckCircle2 },
  pendiente: { label: "Pendiente", className: "bg-amber-50 text-amber-700 ring-amber-200", icon: Clock3 },
  reintento: { label: "Reintento", className: "bg-sky-50 text-sky-700 ring-sky-200", icon: RotateCcw },
  fallido: { label: "Fallida", className: "bg-rose-50 text-rose-700 ring-rose-200", icon: XCircle },
  nuevo: { label: "Nuevo", className: "bg-sky-50 text-sky-700 ring-sky-200", icon: CircleAlert },
  contenido: { label: "Contenida", className: "bg-emerald-50 text-emerald-700 ring-emerald-200", icon: CheckCircle2 },
};

export function StatusIndicator({ value }: { value: string }) {
  const status = statuses[value] ?? { label: value, className: "bg-slate-50 text-slate-600 ring-slate-200", icon: Clock3 };
  const Icon = status.icon;
  return <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ring-inset", status.className)}><Icon className="h-3.5 w-3.5" aria-hidden="true" />{status.label}</span>;
}
