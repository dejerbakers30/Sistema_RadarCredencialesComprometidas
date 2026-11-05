import { useState } from "react";
import { useResets, useManualReset } from "@/hooks/useResets";
import { DataTable } from "@/components/common/DataTable";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function ResetsList() {
  const { data, isLoading, isError } = useResets();
  const manual = useManualReset();
  const canExecute = useCan("execute", "resets");
  const [open, setOpen] = useState(false);
  const [leakId, setLeakId] = useState("");
  const [motivo, setMotivo] = useState("");
  const submit = () => manual.mutate({ leak_hit_id: leakId, motivo }, { onSuccess: () => { setOpen(false); setLeakId(""); setMotivo(""); } });
  return <div className="space-y-7">
    <PageHeader eyebrow="Operación" title="Contenciones" description="Monitorea el resultado de los resets y las acciones de respuesta ejecutadas." actions={canExecute && <Dialog open={open} onOpenChange={setOpen}><DialogTrigger asChild><Button>Contención manual</Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>Forzar contención</DialogTitle></DialogHeader><div className="space-y-4"><Input aria-label="ID de filtración" placeholder="ID de leak_hit" value={leakId} onChange={(e) => setLeakId(e.target.value)} /><Input aria-label="Motivo" placeholder="Motivo (opcional)" value={motivo} onChange={(e) => setMotivo(e.target.value)} /><Button onClick={submit} disabled={!leakId || manual.isPending} className="w-full">{manual.isPending ? "Ejecutando…" : "Ejecutar contención"}</Button></div></DialogContent></Dialog>} />
    <SectionCard title="Registro de contenciones" description={`${data?.length ?? 0} operaciones recientes`}>{isError ? <div role="alert" className="text-sm text-rose-700">No se pudieron cargar las contenciones.</div> : <DataTable loading={isLoading} rows={data ?? []} emptyText="No hay contenciones registradas." columns={[{ key: "leak_hit_id", header: "Filtración", render: (r) => <code className="text-xs text-slate-500">{r.leak_hit_id.slice(0, 8)}…</code> }, { key: "metodo", header: "Método", render: (r) => <span className="capitalize">{r.metodo}</span> }, { key: "resultado", header: "Estado", render: (r) => <StatusIndicator value={r.resultado} /> }, { key: "intentos", header: "Intentos" }, { key: "timestamp", header: "Fecha", render: (r) => formatDateTime(r.timestamp) }, { key: "error_detalle", header: "Resultado", render: (r) => r.error_detalle ?? "Sin incidencias" }]} />}</SectionCard>
  </div>;
}
