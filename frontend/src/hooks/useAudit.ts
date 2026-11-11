import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface AuditEntry {
  id: number;
  ts: string;
  tz: string;
  usuario_email: string | null;
  modulo: string;
  accion: string;
  entidad: string | null;
  entidad_id: string | null;
  resultado: string;
  detalle: Record<string, unknown> | null;
  hash_actual: string;
}

export interface ChainStatus {
  total: number;
  broken: number[];
  ok: boolean;
}

export function useAudit(params: { modulo?: string; desde?: string; hasta?: string; limit?: number }) {
  return useQuery({
    queryKey: ["audit", params],
    queryFn: async () => (await api.get<AuditEntry[]>("/audit", { params })).data,
  });
}

export function useVerifyChain() {
  return useQuery({
    queryKey: ["audit", "verify"],
    queryFn: async () => (await api.get<ChainStatus>("/audit/verify")).data,
  });
}
