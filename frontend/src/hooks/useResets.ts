import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";

export interface Reset {
  id: string;
  leak_hit_id: string;
  usuario_ejecutor: string | null;
  timestamp: string;
  metodo: "automatico" | "manual";
  resultado: "exitoso" | "fallido" | "pendiente" | "reintento";
  intentos: number;
  proximo_intento: string | null;
  error_detalle: string | null;
}

export function useResets(limit = 100) {
  return useQuery({
    queryKey: ["resets", limit],
    queryFn: async () => (await api.get<Reset[]>("/resets", { params: { limit } })).data,
    refetchInterval: 60_000,
  });
}

export function useManualReset() {
  return useMutation({
    mutationFn: async (payload: { leak_hit_id: string; motivo?: string }) =>
      (await api.post<Reset>("/resets/manual", payload)).data,
    onSuccess: (reset) => {
      queryClient.invalidateQueries({ queryKey: ["resets"] });
      queryClient.invalidateQueries({ queryKey: ["leaks"] });
      queryClient.invalidateQueries({ queryKey: ["leak", reset.leak_hit_id] });
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
    },
  });
}
