import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDateTime } from "@/lib/format";

interface Notificacion {
  id: string;
  destinatario: string;
  canal: string;
  plantilla: string | null;
  enviado_en: string | null;
  estado: string;
  error_detalle: string | null;
}

export default function Notifications() {
  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => (await api.get<Notificacion[]>("/notifications")).data,
  });

  if (isLoading) return <div className="text-muted-foreground">Cargando…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Notificaciones</h1>
      <Card>
        <CardHeader><CardTitle>Historial de avisos</CardTitle></CardHeader>
        <CardContent>
          {!data || data.length === 0 ? (
            <EmptyState
              title="Sin notificaciones"
              description="Cuando se detecte una filtración y se notifique al usuario, aparecerá aquí."
            />
          ) : (
            <ul className="divide-y">
              {data.map((n) => (
                <li key={n.id} className="py-3">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{n.destinatario}</span>
                    <span className="text-muted-foreground">{n.estado}</span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {n.canal} · {n.enviado_en ? formatDateTime(n.enviado_en) : "pendiente"}
                  </div>
                  {n.error_detalle && (
                    <div className="text-xs text-destructive mt-1">{n.error_detalle}</div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
