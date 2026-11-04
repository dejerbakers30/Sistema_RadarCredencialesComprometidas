import { useDashboardSummary, useKpis } from "@/hooks/useLeaks";
import { KpiCard } from "@/components/common/KpiCard";
import { TrendLine } from "@/components/charts/TrendLine";
import { SeverityDonut } from "@/components/charts/SeverityDonut";
import { TopBreachesBar } from "@/components/charts/TopBreachesBar";
import { ResetsStackedBar } from "@/components/charts/ResetsStackedBar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const kpis = useKpis();
  const summary = useDashboardSummary(30);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Panel de exposición</h1>

      <div className="grid gap-4 md:grid-cols-4">
        {kpis.isLoading && Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
        {kpis.data && (
          <>
            <KpiCard title="Total filtraciones" value={kpis.data.total} tone="default" />
            <KpiCard title="Pendientes de contención" value={kpis.data.nuevos} tone="warning" />
            <KpiCard title="Contenidas" value={kpis.data.contenidos} tone="success" />
            <KpiCard
              title="MTTC"
              value={kpis.data.mttc_min ? `${kpis.data.mttc_min.toFixed(1)} min` : "—"}
              tone="info"
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Tendencia (30 días)</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <TrendLine data={summary.data.tendencia_diaria} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Distribución por severidad</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <SeverityDonut data={summary.data.por_severidad} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Top breaches</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <TopBreachesBar data={summary.data.top_breaches} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Estado de contenciones</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <ResetsStackedBar data={summary.data.resets_estado} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Usuarios reincidentes</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {summary.data?.reincidentes.map((r) => (
              <li key={r.email} className="py-2 flex justify-between text-sm">
                <span>{r.email}</span>
                <span className="text-muted-foreground">{r.total} filtraciones</span>
              </li>
            ))}
            {summary.data?.reincidentes.length === 0 && (
              <li className="py-4 text-center text-muted-foreground text-sm">
                Sin reincidencias detectadas
              </li>
            )}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
