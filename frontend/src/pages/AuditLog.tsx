import { useState } from "react";
import { CheckCircle2, ShieldCheck, XCircle } from "lucide-react";
import { useAudit, useVerifyChain } from "@/hooks/useAudit";
import { DataTable } from "@/components/common/DataTable";
import { FilterBar } from "@/components/common/FilterBar";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { formatDateTime } from "@/lib/format";

export default function AuditLog() {
  const [modulo, setModulo] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [hash, setHash] = useState<string | null>(null);
  const { data, isLoading, isError } = useAudit({ modulo: modulo || undefined, desde: desde ? `${desde}T00:00:00Z` : undefined, hasta: hasta ? `${hasta}T23:59:59Z` : undefined, limit: 200 });
  const chain = useVerifyChain();
  return <div className="space-y-7">
    <PageHeader eyebrow="Análisis" title="Bitácora de auditoría" description="Consulta los eventos inmutables registrados por el sistema y verifica su integridad." actions={<Button variant="outline" onClick={() => chain.refetch()} disabled={chain.isFetching}><ShieldCheck className="h-4 w-4" />{chain.isFetching ? "Verificando…" : "Verificar integridad"}</Button>} />
    <div className={`flex items-center gap-3 rounded-xl border px-5 py-4 ${chain.data?.ok ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-rose-200 bg-rose-50 text-rose-800"}`} role="status">{chain.data?.ok ? <CheckCircle2 className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}<div><p className="font-semibold">{chain.data ? (chain.data.ok ? "Cadena íntegra" : "Integridad comprometida") : "Integridad pendiente de verificación"}</p>{chain.data && <p className="text-xs opacity-80">{chain.data.total} registros revisados{!chain.data.ok && ` · ${chain.data.broken.length} incidencias`}</p>}</div></div>
    <FilterBar onClear={() => { setModulo(""); setDesde(""); setHasta(""); }}><Input aria-label="Filtrar por módulo" placeholder="Módulo" value={modulo} onChange={(e) => setModulo(e.target.value)} className="w-44" /><Input aria-label="Fecha desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} className="w-40" /><Input aria-label="Fecha hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} className="w-40" /></FilterBar>
    <SectionCard title="Eventos registrados" description={`${data?.length ?? 0} eventos recientes`}>{isError ? <div role="alert" className="text-sm text-rose-700">No se pudo cargar la bitácora.</div> : <DataTable loading={isLoading} rows={data ?? []} emptyText="No hay eventos para los filtros seleccionados." columns={[{ key: "ts", header: "Fecha", render: (r) => formatDateTime(r.ts) }, { key: "usuario_email", header: "Usuario", render: (r) => r.usuario_email ?? "Sistema" }, { key: "modulo", header: "Módulo" }, { key: "accion", header: "Acción" }, { key: "resultado", header: "Resultado", render: (r) => <StatusIndicator value={r.resultado === "ok" ? "exitoso" : "fallido"} /> }, { key: "entidad", header: "Entidad", render: (r) => r.entidad ?? "—" }, { key: "hash_actual", header: "Hash", render: (r) => <button className="font-mono text-xs text-primary hover:underline" onClick={() => setHash(r.hash_actual)}>{r.hash_actual.slice(0, 12)}…</button> }]} />}</SectionCard>
    <Dialog open={Boolean(hash)} onOpenChange={(open) => !open && setHash(null)}><DialogContent><DialogHeader><DialogTitle>Hash completo</DialogTitle></DialogHeader><code className="break-all rounded-lg bg-slate-50 p-4 text-xs text-slate-700">{hash}</code></DialogContent></Dialog>
  </div>;
}
