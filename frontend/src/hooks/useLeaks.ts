import { keepPreviousData, useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";

export interface Kpis {
  total: number;
  nuevos: number;
  contenidos: number;
  mttc_min: number | null;
}

export interface DashboardSummary {
  tendencia_diaria: { fecha: string; total: number }[];
  por_severidad: { severidad: string; total: number }[];
  top_breaches: { breach: string; total: number }[];
  resets_estado: { resultado: string; total: number }[];
  reincidentes: { email: string; total: number }[];
}

export interface Leak {
  id: string;
  email_corporativo: string;
  usuario_id: string | null;
  breach_origen: string;
  breach_dominio: string | null;
  fecha_breach: string | null;
  fecha_deteccion: string;
  severidad: "baja" | "media" | "alta" | "critica";
  fuente_detalle: string | null;
  datos_expuestos: string[] | null;
  estado: "nuevo" | "contenido" | "resuelto" | "falso_positivo";
  fecha_contencion: string | null;
  hash_canonico: string;
}

export interface LeaksFilter {
  estado?: string;
  email?: string;
  limit?: number;
  offset?: number;
}

export function useKpis() {
  return useQuery({
    queryKey: ["kpis"],
    queryFn: async () => (await api.get<Kpis>("/leaks/kpis")).data,
    refetchInterval: 60_000,
  });
}

export function useDashboardSummary(dias = 30) {
  return useQuery({
    queryKey: ["dashboard", "summary", dias],
    queryFn: async () =>
      (await api.get<DashboardSummary>("/dashboard/summary", { params: { dias } })).data,
    refetchInterval: 120_000,
  });
}

export function useLeaks(filter: LeaksFilter) {
  return useQuery({
    queryKey: ["leaks", filter],
    queryFn: async () => (await api.get<Leak[]>("/leaks", { params: filter })).data,
    placeholderData: keepPreviousData,
  });
}

export function useLeak(id: string) {
  return useQuery({
    queryKey: ["leak", id],
    queryFn: async () => (await api.get<Leak>(`/leaks/${id}`)).data,
    enabled: !!id,
  });
}

export function useUpdateLeak() {
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Leak> }) =>
      (await api.patch<Leak>(`/leaks/${id}`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leaks"] });
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
    },
  });
}
