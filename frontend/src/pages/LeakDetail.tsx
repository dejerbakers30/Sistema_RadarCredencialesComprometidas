import { useParams } from "react-router-dom";
import { useLeak, useUpdateLeak } from "@/hooks/useLeaks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Button } from "@/components/ui/button";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function LeakDetail() {
  const { id = "" } = useParams();
  const { data, isLoading } = useLeak(id);
  const update = useUpdateLeak();
  const canWrite = useCan("write", "leaks");
  const canExecute = useCan("execute", "resets");

  if (isLoading || !data) return <div className="text-muted-foreground">Cargando…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Detalle de filtración</h1>

      <Card>
        <CardHeader><CardTitle>{data.breach_origen}</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <Field label="Email" value={data.email_corporativo} />
          <Field label="Dominio del breach" value={data.breach_dominio ?? "—"} />
          <Field label="Fecha del breach" value={data.fecha_breach ?? "—"} />
          <Field label="Detectado" value={formatDateTime(data.fecha_deteccion)} />
          <Field label="Severidad" value={<SeverityBadge value={data.severidad} />} />
          <Field label="Estado" value={<StatusBadge value={data.estado} />} />
          <Field
            label="Datos expuestos"
            value={data.datos_expuestos?.join(", ") ?? "No especificado"}
          />
          <Field label="Fuente" value={data.fuente_detalle ?? "—"} />
          <Field
            label="Contenido en"
            value={data.fecha_contencion ? formatDateTime(data.fecha_contencion) : "Pendiente"}
          />
        </CardContent>
      </Card>

      <div className="flex gap-3">
        {canWrite && data.estado !== "falso_positivo" && (
          <Button
            variant="outline"
            onClick={() => update.mutate({ id: data.id, data: { estado: "falso_positivo" } })}
          >
            Marcar como falso positivo
          </Button>
        )}
        {canExecute && data.estado !== "contenido" && (
          <Button
            onClick={() => update.mutate({ id: data.id, data: { estado: "contenido" } })}
          >
            Forzar contención manual
          </Button>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-muted-foreground text-xs uppercase tracking-wide">{label}</div>
      <div className="mt-1">{value}</div>
    </div>
  );
}
