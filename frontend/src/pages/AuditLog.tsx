import { useState } from "react";
import { useAudit, useVerifyChain } from "@/hooks/useAudit";
import { DataTable } from "@/components/common/DataTable";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/format";

export default function AuditLog() {
  const [modulo, setModulo] = useState("");
  const [limit] = useState(200);
  const { data, isLoading } = useAudit({ modulo: modulo || undefined, limit });
  const chain = useVerifyChain();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Bitácora de auditoría</h1>
        {chain.data && (
          <Badge variant={chain.data.ok ? "default" : "destructive"}>
            Cadena: {chain.data.ok ? "íntegra" : `rota (${chain.data.broken.length})`}
          </Badge>
        )}
      </div>

      <Input
        placeholder="Filtrar por módulo (auth, leaks, resets…)"
        value={modulo}
        onChange={(e) => setModulo(e.target.value)}
        className="max-w-xs"
      />

      <DataTable
        loading={isLoading}
        rows={data ?? []}
        columns={[
          { key: "ts", header: "Fecha", render: (r) => formatDateTime(r.ts) },
          { key: "usuario_email", header: "Usuario", render: (r) => r.usuario_email ?? "sistema" },
          { key: "modulo", header: "Módulo" },
          { key: "accion", header: "Acción" },
          { key: "resultado", header: "Resultado" },
          { key: "entidad", header: "Entidad", render: (r) => r.entidad ?? "—" },
          { key: "hash_actual", header: "Hash", render: (r) => r.hash_actual.slice(0, 12) + "…" },
        ]}
      />
    </div>
  );
}
