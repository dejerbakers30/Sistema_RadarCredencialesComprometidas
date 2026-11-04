import { useState } from "react";
import { useGenerateReport, downloadReport } from "@/hooks/useReports";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api";

export default function Reports() {
  const [tipo, setTipo] = useState<"operacional" | "gestion" | "ejecutivo">("operacional");
  const [formato, setFormato] = useState<"pdf" | "docx" | "xlsx">("pdf");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const gen = useGenerateReport();
  const toast = useToast();

  const onSubmit = () => {
    gen.mutate(
      { tipo, formato, periodo_desde: desde, periodo_hasta: hasta },
      {
        onSuccess: (rep) => {
          toast.push({ title: "Reporte generado", description: `${rep.tipo} / ${rep.formato}`, tone: "success" });
          downloadReport(rep.id, `${rep.tipo}_${rep.periodo_desde}_${rep.periodo_hasta}.${rep.formato}`);
        },
        onError: (e) => toast.push({ title: "Error", description: extractErrorMessage(e), tone: "danger" }),
      }
    );
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Reportes</h1>
      <Card>
        <CardHeader><CardTitle>Generar reporte</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div>
            <label className="text-sm font-medium">Tipo</label>
            <Select value={tipo} onValueChange={(v) => setTipo(v as any)}>
              <option value="operacional">Operacional (PDF)</option>
              <option value="gestion">Gestión (Word)</option>
              <option value="ejecutivo">Ejecutivo (Excel)</option>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium">Formato</label>
            <Select value={formato} onValueChange={(v) => setFormato(v as any)}>
              <option value="pdf">PDF</option>
              <option value="docx">Word</option>
              <option value="xlsx">Excel</option>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium">Desde</label>
            <Input type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
          </div>
          <div>
            <label className="text-sm font-medium">Hasta</label>
            <Input type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
          </div>
          <div className="md:col-span-4 flex justify-end">
            <Button onClick={onSubmit} disabled={!desde || !hasta || gen.isPending}>
              {gen.isPending ? "Generando…" : "Generar y descargar"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
