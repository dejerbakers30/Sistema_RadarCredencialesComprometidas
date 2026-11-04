import { useSources } from "@/hooks/useSources";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/format";

export default function Sources() {
  const { data, isLoading } = useSources();
  if (isLoading) return <div className="text-muted-foreground">Cargando…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Fuentes y dominios</h1>

      <Card>
        <CardHeader><CardTitle>Fuentes de datos</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.fuentes.map((f) => (
              <li key={f.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-medium">{f.nombre}</div>
                  <div className="text-xs text-muted-foreground">
                    Última consulta: {f.ultima_consulta ? formatDateTime(f.ultima_consulta) : "—"}
                  </div>
                </div>
                <Badge variant={f.activa ? "default" : "destructive"}>
                  {f.activa ? "Activa" : "Inactiva"}
                </Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Dominios monitoreados</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.dominios.map((d) => (
              <li key={d.id} className="py-3 flex items-center justify-between">
                <span className="font-medium">{d.dominio}</span>
                <Badge variant={d.activo ? "default" : "destructive"}>
                  {d.activo ? "Activo" : "Inactivo"}
                </Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
