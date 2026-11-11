import { useState } from "react";
import { useParams } from "react-router-dom";
import { useLeak, useUpdateLeak } from "@/hooks/useLeaks";
import { useManualReset } from "@/hooks/useResets";
import { extractErrorMessage } from "@/lib/api";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { ErrorState, LoadingState, PageHeader, SectionCard } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function LeakDetail() {
  const { id = "" } = useParams();
  const { data, isLoading, isError } = useLeak(id);
  const update = useUpdateLeak();
  const manualReset = useManualReset();
  const canWrite = useCan("write", "leaks");
  const canExecute = useCan("execute", "resets");
  const [confirm, setConfirm] = useState<"false-positive" | "containment" | null>(null);
  if (isLoading) return <LoadingState label="Cargando detalle de la filtración…" />;
  if (isError || !data) return <ErrorState message="No se pudo cargar la filtración solicitada." />;
  return <div className="space-y-7">
    <PageHeader eyebrow="Filtración" title={data.breach_origen} description={`Exposición detectada para ${data.email_corporativo}`} />
    <div className="grid gap-5 lg:grid-cols-2">
      <SectionCard title="Identificación"><div className="grid gap-5 sm:grid-cols-2"><Field label="Correo" value={data.email_corporativo} /><Field label="Dominio del breach" value={data.breach_dominio ?? "—"} /><Field label="Fuente" value={data.fuente_detalle ?? "—"} /><Field label="Estado" value={<StatusIndicator value={data.estado} />} /></div></SectionCard>
      <SectionCard title="Exposición"><div className="grid gap-5 sm:grid-cols-2"><Field label="Fecha del breach" value={data.fecha_breach ?? "—"} /><Field label="Fecha de detección" value={formatDateTime(data.fecha_deteccion)} /><Field label="Datos comprometidos" value={data.datos_expuestos?.join(", ") ?? "No especificado"} /><Field label="Severidad" value={<SeverityBadge value={data.severidad} />} /></div></SectionCard>
      <SectionCard title="Respuesta" className="lg:col-span-2"><div className="grid gap-5 sm:grid-cols-3"><Field label="Estado de contención" value={<StatusIndicator value={data.estado === "contenido" ? "exitoso" : "pendiente"} />} /><Field label="Fecha de contención" value={data.fecha_contencion ? formatDateTime(data.fecha_contencion) : "Pendiente"} /><Field label="Identificador" value={<code className="break-all text-xs text-slate-500">{data.hash_canonico}</code>} /></div></SectionCard>
    </div>
    <div className="flex flex-wrap gap-3">{canWrite && data.estado !== "falso_positivo" && <Button variant="outline" onClick={() => setConfirm("false-positive")}>Marcar como falso positivo</Button>}{canExecute && data.estado !== "contenido" && <Button onClick={() => setConfirm("containment")} disabled={manualReset.isPending}>{manualReset.isPending ? "Ejecutando contención…" : "Forzar contención manual"}</Button>}</div>
    {manualReset.isError && <p role="alert" className="text-sm text-rose-700">{extractErrorMessage(manualReset.error)}</p>}
    {manualReset.data && <p role="status" className="text-sm text-emerald-700">Contención registrada: {manualReset.data.resultado}</p>}
    <ConfirmDialog open={confirm === "false-positive"} onOpenChange={(open) => !open && setConfirm(null)} title="Marcar falso positivo" description="Esta exposición dejará de aparecer como pendiente de respuesta. ¿Deseas continuar?" confirmLabel="Marcar falso positivo" loading={update.isPending} onConfirm={() => update.mutate({ id: data.id, data: { estado: "falso_positivo" } }, { onSuccess: () => setConfirm(null) })} />
    <ConfirmDialog open={confirm === "containment"} onOpenChange={(open) => !open && setConfirm(null)} title="Forzar contención" description="Se ejecutará la operación de contención para esta cuenta. ¿Deseas continuar?" confirmLabel="Ejecutar contención" loading={manualReset.isPending} onConfirm={() => manualReset.mutate({ leak_hit_id: data.id }, { onSuccess: () => setConfirm(null) })} />
  </div>;
}

function Field({ label, value }: { label: string; value: React.ReactNode }) { return <div><div className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</div><div className="mt-1 text-sm text-slate-700">{value}</div></div>; }
