import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface ReportRow {
  id: string;
  tipo: string;
  formato: string;
  periodo_desde: string;
  periodo_hasta: string;
  generado_en: string;
  hash_archivo: string;
}

export interface ReportRequest {
  tipo: "operacional" | "gestion" | "ejecutivo";
  formato: "pdf" | "docx" | "xlsx";
  periodo_desde: string;
  periodo_hasta: string;
}

export function useGenerateReport() {
  return useMutation({
    mutationFn: async (payload: ReportRequest) =>
      (await api.post<ReportRow>("/reports", payload)).data,
  });
}

export async function downloadReport(id: string, filename: string) {
  const resp = await api.get(`/reports/${id}/download`, { responseType: "blob" });
  const url = window.URL.createObjectURL(resp.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}
