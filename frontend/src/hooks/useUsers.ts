import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";

export interface User {
  id: string;
  email: string;
  nombre: string;
  activo: boolean;
  mfa_enabled: boolean;
}

export function useUsers() {
  return useQuery({
    queryKey: ["users"],
    queryFn: async () => (await api.get<User[]>("/users")).data,
  });
}

export function useCreateUser() {
  return useMutation({
    mutationFn: async (payload: { email: string; nombre: string; rol: string; password?: string }) =>
      (await api.post<User>("/users", payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser() {
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<User> & { rol?: string; password?: string } }) =>
      (await api.patch<User>(`/users/${id}`, data)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}
