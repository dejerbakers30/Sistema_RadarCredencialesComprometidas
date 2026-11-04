import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { api, extractErrorMessage } from "@/lib/api";
import { useAuthStore, type AuthUser } from "@/stores/authStore";

interface LoginPayload { email: string; password: string }
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  mfa_required: boolean;
}

export function useLogin() {
  const { setTokens, setUser, setMfaPending } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const { data } = await api.post<TokenResponse>("/auth/login", payload);
      return data;
    },
    onSuccess: async (data, variables) => {
      if (data.mfa_required) {
        setMfaPending(variables.email);
        navigate("/mfa");
        return;
      }
      setTokens(data.access_token, data.refresh_token);
      const me = await api.get<AuthUser>("/auth/me");
      setUser(me.data);
      navigate("/dashboard");
    },
  });
}

export function useMfaVerify() {
  const { setTokens, setUser, setMfaPending } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async (payload: { email: string; code: string }) => {
      const { data } = await api.post<TokenResponse>("/auth/mfa/verify", payload);
      return data;
    },
    onSuccess: async (data) => {
      setTokens(data.access_token, data.refresh_token);
      const me = await api.get<AuthUser>("/auth/me");
      setUser(me.data);
      setMfaPending(null);
      navigate("/dashboard");
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  return useCallback(() => {
    logout();
    navigate("/login");
  }, [logout, navigate]);
}

export function useAuth() {
  return useAuthStore();
}

export { extractErrorMessage };
