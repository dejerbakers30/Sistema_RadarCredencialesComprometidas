import { AlertTriangle, CheckCircle2, Clock3, ShieldCheck } from "lucide-react";
import { useDashboardSummary, useKpis } from "@/hooks/useLeaks";
import { KpiCard } from "@/components/common/KpiCard";
import { TrendLine } from "@/components/charts/TrendLine";
import { SeverityDonut } from "@/components/charts/SeverityDonut";
import { TopBreachesBar } from "@/components/charts/TopBreachesBar";
import { ResetsStackedBar } from "@/components/charts/ResetsStackedBar";
import { EmptyState, ErrorState, LoadingState, PageHeader, SectionCard } from "@/components/common/PageHeader";

export default function Dashboard() {
  const kpis = useKpis();
  const summary = useDashboardSummary(30);
  const loading = kpis.isLoading || summary.isLoading;

  return <div className="space-y-7">
    <PageHeader eyebrow="Centro de operaciones" title="Panel de exposición de credenciales" description="Supervisa filtraciones detectadas, contenciones y señales de riesgo de las últimas semanas." />
    {kpis.isError || summary.isError ? <ErrorState message="No fue posible cargar todos los indicadores operacionales." /> : null}
    {loading ? <LoadingState label="Cargando indicadores y tendencias…" /> : <>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard title="Total filtraciones" value={kpis.data?.total ?? "—"} helper="Registros detectados" icon={AlertTriangle} />
        <KpiCard title="Pendientes de contención" value={kpis.data?.nuevos ?? "—"} helper="Requieren seguimiento" tone="warning" icon={Clock3} />
        <KpiCard title="Contenidas" value={kpis.data?.contenidos ?? "—"} helper="Respuesta completada" tone="success" icon={CheckCircle2} />
        <KpiCard title="MTTC" value={kpis.data?.mttc_min ? `${kpis.data.mttc_min.toFixed(1)} min` : "—"} helper="Tiempo medio de contención" tone="info" icon={ShieldCheck} />
      </div>
      {summary.data && <div className="grid gap-5 xl:grid-cols-2">
        <SectionCard title="Tendencia temporal" description="Exposiciones detectadas durante los últimos 30 días"><ChartOrEmpty hasData={summary.data.tendencia_diaria.length > 0}><TrendLine data={summary.data.tendencia_diaria} /></ChartOrEmpty></SectionCard>
        <SectionCard title="Distribución por severidad" description="Clasificación de las exposiciones identificadas"><ChartOrEmpty hasData={summary.data.por_severidad.length > 0}><SeverityDonut data={summary.data.por_severidad} /></ChartOrEmpty></SectionCard>
        <SectionCard title="Breaches más frecuentes" description="Principales fuentes de exposición"><ChartOrEmpty hasData={summary.data.top_breaches.length > 0}><TopBreachesBar data={summary.data.top_breaches} /></ChartOrEmpty></SectionCard>
        <SectionCard title="Estado de contenciones" description="Resultado de las acciones ejecutadas"><ChartOrEmpty hasData={summary.data.resets_estado.length > 0}><ResetsStackedBar data={summary.data.resets_estado} /></ChartOrEmpty></SectionCard>
      </div>}
      <SectionCard title="Usuarios reincidentes" description="Cuentas que aparecen en más de una filtración"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-100 text-xs uppercase tracking-wide text-slate-400"><tr><th className="pb-3 font-semibold">Usuario</th><th className="pb-3 text-right font-semibold">Filtraciones</th></tr></thead><tbody className="divide-y divide-slate-100">{summary.data?.reincidentes.map((r) => <tr key={r.email}><td className="py-3 font-medium text-slate-700">{r.email}</td><td className="py-3 text-right text-slate-500">{r.total}</td></tr>)}</tbody></table></div>{summary.data?.reincidentes.length === 0 && <EmptyState title="No hay reincidencias" description="No se han detectado usuarios con múltiples exposiciones en el período consultado." />}</SectionCard>
    </>}
  </div>;
}

function ChartOrEmpty({ hasData, children }: { hasData: boolean; children: React.ReactNode }) {
  return hasData ? <div className="h-64 w-full">{children}</div> : <EmptyState title="Sin datos para mostrar" description="El endpoint no devolvió registros para este período." />;
}
