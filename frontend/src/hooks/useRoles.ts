import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export interface RoleInfo {
  id: number;
  nombre: string;
  descripcion: string | null;
  permisos: { modulo: string; accion: string }[];
  usuarios: string[];
}

export function useRoles() {
  return useQuery({ queryKey: ["roles"], queryFn: async () => (await api.get<RoleInfo[]>("/roles")).data });
}
