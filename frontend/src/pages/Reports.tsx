import { useState } from "react";
import { BarChart3, FileSpreadsheet, FileText, ShieldCheck } from "lucide-react";
import { useGenerateReport, downloadReport } from "@/hooks/useReports";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";

const reportTypes = [
  { value: "operacional", label: "Operacional", format: "PDF", description: "Detalle técnico y operativo.", icon: ShieldCheck },
  { value: "gestion", label: "Gestión", format: "DOCX", description: "Indicadores para responsables del área.", icon: FileText },
  { value: "ejecutivo", label: "Ejecutivo", format: "XLSX", description: "Resumen de KPIs para dirección.", icon: FileSpreadsheet },
] as const;

export default function Reports() {
  const [tipo, setTipo] = useState<(typeof reportTypes)[number]["value"]>("operacional");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const gen = useGenerateReport();
  const toast = useToast();
  const selected = reportTypes.find((item) => item.value === tipo) ?? reportTypes[0];
  const invalidRange = Boolean(desde && hasta && desde > hasta);
  const onSubmit = () => {
    if (!desde || !hasta || invalidRange) return;
    const formato = selected.value === "operacional" ? "pdf" : selected.value === "gestion" ? "docx" : "xlsx";
    gen.mutate({ tipo: selected.value, formato, periodo_desde: desde, periodo_hasta: hasta }, { onSuccess: (rep) => { toast.push({ title: "Reporte generado", description: `${rep.tipo} / ${rep.formato}`, tone: "success" }); downloadReport(rep.id, `${rep.tipo}_${rep.periodo_desde}_${rep.periodo_hasta}.${rep.formato}`); }, onError: (e) => toast.push({ title: "Error al generar", description: extractErrorMessage(e), tone: "danger" }) });
  };
  return <div className="space-y-7">
    <PageHeader eyebrow="Análisis" title="Reportes" description="Genera entregables operativos, de gestión o ejecutivos a partir de datos reales del sistema." />
    <SectionCard title="Selecciona el tipo de reporte" description="El formato se asigna automáticamente para evitar combinaciones incompatibles."><div className="grid gap-4 md:grid-cols-3">{reportTypes.map((item) => { const Icon = item.icon; return <button key={item.value} type="button" onClick={() => setTipo(item.value)} className={`rounded-xl border p-5 text-left transition ${tipo === item.value ? "border-primary bg-blue-50 ring-2 ring-blue-100" : "border-slate-200 bg-white hover:border-blue-200 hover:bg-slate-50"}`}><div className="flex items-start justify-between"><div className={`rounded-lg p-2 ${tipo === item.value ? "bg-primary text-white" : "bg-slate-100 text-slate-500"}`}><Icon className="h-5 w-5" /></div><span className="rounded-full bg-white px-2 py-1 text-xs font-bold text-slate-500 ring-1 ring-slate-200">{item.format}</span></div><h2 className="mt-5 font-semibold text-slate-900">{item.label}</h2><p className="mt-1 text-sm text-slate-500">{item.description}</p></button>; })}</div></SectionCard>
    <Card className="rounded-xl border-slate-200 shadow-sm"><CardContent className="p-5"><div className="mb-5 flex items-center gap-3"><div className="rounded-lg bg-blue-50 p-2 text-primary"><BarChart3 className="h-5 w-5" /></div><div><h2 className="font-semibold text-slate-900">Período del reporte</h2><p className="text-sm text-slate-500">{selected.label} se generará en formato {selected.format}.</p></div></div><div className="grid gap-4 sm:grid-cols-2"><div><label htmlFor="desde" className="mb-1.5 block text-sm font-medium text-slate-700">Fecha desde</label><Input id="desde" type="date" value={desde} onChange={(e) => setDesde(e.target.value)} /></div><div><label htmlFor="hasta" className="mb-1.5 block text-sm font-medium text-slate-700">Fecha hasta</label><Input id="hasta" type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} /></div></div>{invalidRange && <p role="alert" className="mt-3 text-sm text-rose-700">La fecha desde debe ser anterior o igual a la fecha hasta.</p>}<div className="mt-5 flex justify-end"><Button onClick={onSubmit} disabled={!desde || !hasta || invalidRange || gen.isPending}>{gen.isPending ? "Generando…" : "Generar y descargar"}</Button></div></CardContent></Card>
  </div>;
}
