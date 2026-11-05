import { useState } from "react";
import { Bell, Mail, MessageSquare } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { EmptyState, PageHeader, SectionCard } from "@/components/common/PageHeader";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { FilterBar } from "@/components/common/FilterBar";
import { Pagination } from "@/components/common/Pagination";
import { Select } from "@/components/ui/select";
import { formatDateTime } from "@/lib/format";

interface Notificacion { id: string; destinatario: string; canal: string; plantilla: string | null; enviado_en: string | null; estado: string; error_detalle: string | null }
interface NotificationPage { items: Notificacion[]; total: number; limit: number; offset: number }

export default function Notifications() {
  const [estado, setEstado] = useState("");
  const [canal, setCanal] = useState("");
  const [page, setPage] = useState(0);
  const limit = 20;
  const query = useQuery({ queryKey: ["notifications", estado, canal, page], queryFn: async () => (await api.get<NotificationPage>("/notifications", { params: { estado: estado || undefined, canal: canal || undefined, limit, offset: page * limit } })).data });
  return <div className="space-y-7">
    <PageHeader eyebrow="Cuenta" title="Notificaciones" description="Consulta el estado de las comunicaciones emitidas por el sistema." />
    <FilterBar onClear={() => { setEstado(""); setCanal(""); setPage(0); }}><Select aria-label="Filtrar por estado" value={estado} onValueChange={(v) => { setEstado(v); setPage(0); }}><option value="">Todos los estados</option><option value="enviado">Enviado</option><option value="fallido">Fallido</option><option value="pendiente">Pendiente</option></Select><Select aria-label="Filtrar por canal" value={canal} onValueChange={(v) => { setCanal(v); setPage(0); }}><option value="">Todos los canales</option><option value="email">Email</option><option value="slack">Slack</option><option value="teams">Teams</option></Select></FilterBar>
    <SectionCard title="Historial de avisos" description={query.data ? `${query.data.total} notificaciones` : "Comunicaciones recientes"}>{query.isLoading ? <div className="py-8 text-center text-sm text-slate-500">Cargando notificaciones…</div> : query.isError ? <div role="alert" className="text-sm text-rose-700">No se pudieron cargar las notificaciones.</div> : !query.data?.items.length ? <EmptyState icon={Bell} title="Sin notificaciones" description="Cuando se detecte una filtración y se notifique al usuario, aparecerá aquí." /> : <><div className="space-y-3">{query.data.items.map((n) => <article key={n.id} className="flex gap-4 rounded-lg border border-slate-100 p-4 hover:bg-slate-50"><div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-primary">{n.canal === "email" ? <Mail className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center justify-between gap-2"><h3 className="text-sm font-semibold text-slate-800">{n.plantilla ?? "Notificación de seguridad"}</h3><StatusIndicator value={n.estado} /></div><p className="mt-1 text-xs text-slate-500">{n.destinatario} · {n.canal} · {n.enviado_en ? formatDateTime(n.enviado_en) : "Pendiente de envío"}</p>{n.error_detalle && <p className="mt-2 text-xs text-rose-700">{n.error_detalle}</p>}</div></article>)}</div><Pagination page={page} setPage={setPage} hasMore={query.data.offset + query.data.items.length < query.data.total} pageSize={limit} total={query.data.total} /></>}</SectionCard>
  </div>;
}
