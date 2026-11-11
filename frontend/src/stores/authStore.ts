import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface AuthUser {
  id: string;
  email: string;
  nombre: string;
  rol: "admin" | "soc_analyst" | "auditor" | "end_user";
  mfa_enabled: boolean;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  mfaPendingEmail: string | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (u: AuthUser | null) => void;
  setMfaPending: (email: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      mfaPendingEmail: null,
      setTokens: (access, refresh) => set({ accessToken: access, refreshToken: refresh }),
      setUser: (user) => set({ user }),
      setMfaPending: (email) => set({ mfaPendingEmail: email }),
      logout: () =>
        set({ accessToken: null, refreshToken: null, user: null, mfaPendingEmail: null }),
    }),
    {
      name: "radar-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
        user: s.user,
      }),
    }
  )
);
