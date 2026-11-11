import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface Fuente {
  id: number;
  nombre: string;
  activa: boolean;
  ultima_consulta: string | null;
}
export interface Dominio {
  id: number;
  dominio: string;
  activo: boolean;
}
export interface SourcesResponse {
  fuentes: Fuente[];
  dominios: Dominio[];
}

export function useSources() {
  return useQuery({
    queryKey: ["sources"],
    queryFn: async () => (await api.get<SourcesResponse>("/sources")).data,
  });
}
