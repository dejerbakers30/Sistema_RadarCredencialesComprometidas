import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useLeaks } from "@/hooks/useLeaks";
import { DataTable } from "@/components/common/DataTable";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { FilterBar } from "@/components/common/FilterBar";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";
import { Select } from "@/components/ui/select";
import { formatDateTime } from "@/lib/format";

export default function LeaksList() {
  const [estado, setEstado] = useState("");
  const [emailInput, setEmailInput] = useState("");
  const [email, setEmail] = useState("");
  const [page, setPage] = useState(0);
  const limit = 25;
  useEffect(() => { const timer = window.setTimeout(() => { setEmail(emailInput); setPage(0); }, 350); return () => window.clearTimeout(timer); }, [emailInput]);
  const { data, isLoading, isError } = useLeaks({ estado: estado || undefined, email: email || undefined, limit, offset: page * limit });
  const clear = () => { setEmailInput(""); setEmail(""); setEstado(""); setPage(0); };
  return <div className="space-y-7">
    <PageHeader eyebrow="Operación" title="Filtraciones detectadas" description="Revisa las exposiciones identificadas y abre el detalle para coordinar la respuesta." />
    <FilterBar search={emailInput} onSearch={setEmailInput} onClear={clear}>
      <Select aria-label="Filtrar por estado" value={estado} onValueChange={(v) => { setEstado(v); setPage(0); }} className="min-w-44"><option value="">Todos los estados</option><option value="nuevo">Nuevo</option><option value="contenido">Contenida</option><option value="resuelto">Resuelta</option><option value="falso_positivo">Falso positivo</option></Select>
    </FilterBar>
    <SectionCard title="Registro de exposiciones" description={`${data?.length ?? 0} registros en esta página`}>
      {isError ? <div role="alert" className="text-sm text-rose-700">Error al cargar filtraciones.</div> : <DataTable loading={isLoading} rows={data ?? []} emptyText="No hay filtraciones con estos filtros." columns={[
        { key: "email_corporativo", header: "Usuario / correo", render: (r) => <Link to={`/leaks/${r.id}`} className="font-semibold text-primary hover:underline">{r.email_corporativo}</Link> },
        { key: "breach_origen", header: "Breach", render: (r) => <span className="font-medium text-slate-700">{r.breach_origen}</span> },
        { key: "datos_expuestos", header: "Datos expuestos", render: (r) => r.datos_expuestos?.slice(0, 2).join(", ") || "No especificado" },
        { key: "fecha_breach", header: "Fecha breach", render: (r) => r.fecha_breach ?? "—" },
        { key: "severidad", header: "Severidad", render: (r) => <SeverityBadge value={r.severidad} /> },
        { key: "estado", header: "Estado", render: (r) => <StatusIndicator value={r.estado} /> },
        { key: "fecha_deteccion", header: "Detectado", render: (r) => formatDateTime(r.fecha_deteccion) },
      ]} pagination={{ page, setPage, pageSize: limit, hasMore: (data?.length ?? 0) === limit }} />}
    </SectionCard>
  </div>;
}
