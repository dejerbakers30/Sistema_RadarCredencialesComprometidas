import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeaks } from "@/hooks/useLeaks";
import { DataTable } from "@/components/common/DataTable";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { formatDateTime } from "@/lib/format";

export default function LeaksList() {
  const [estado, setEstado] = useState<string>("");
  const [email, setEmail] = useState("");
  const [page, setPage] = useState(0);
  const limit = 25;

  const { data, isLoading, isError } = useLeaks({
    estado: estado || undefined,
    email: email || undefined,
    limit,
    offset: page * limit,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Filtraciones detectadas</h1>
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Buscar por email…"
          value={email}
          onChange={(e) => { setEmail(e.target.value); setPage(0); }}
          className="max-w-xs"
        />
        <Select value={estado} onValueChange={(v) => { setEstado(v); setPage(0); }}>
          <option value="">Todos los estados</option>
          <option value="nuevo">Nuevo</option>
          <option value="contenido">Contenido</option>
          <option value="resuelto">Resuelto</option>
          <option value="falso_positivo">Falso positivo</option>
        </Select>
      </div>

      <DataTable
        loading={isLoading}
        error={isError ? "Error al cargar filtraciones" : undefined}
        rows={data ?? []}
        columns={[
          {
            key: "email_corporativo",
            header: "Email",
            render: (r) => (
              <Link to={`/leaks/${r.id}`} className="text-primary hover:underline">
                {r.email_corporativo}
              </Link>
            ),
          },
          { key: "breach_origen", header: "Breach" },
          { key: "fecha_breach", header: "Fecha breach", render: (r) => r.fecha_breach ?? "—" },
          { key: "severidad", header: "Severidad", render: (r) => <SeverityBadge value={r.severidad} /> },
          { key: "estado", header: "Estado", render: (r) => <StatusBadge value={r.estado} /> },
          {
            key: "fecha_deteccion",
            header: "Detectado",
            render: (r) => formatDateTime(r.fecha_deteccion),
          },
        ]}
        pagination={{ page, setPage, pageSize: limit, hasMore: (data?.length ?? 0) === limit }}
      />
    </div>
  );
}
