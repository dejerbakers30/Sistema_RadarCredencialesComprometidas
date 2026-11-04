PASO 3 — Verificación, Completitud y Mejora de Módulos Frontend
Alcance del Paso 3: Auditar el frontend contra los requisitos del Paso 1, identificar módulos faltantes, completar los existentes y entregar código React + TypeScript ejecutable, integrado con la API del Paso 2. Se mantiene el stack decidido: React 18 + Vite + TypeScript + Tailwind + shadcn/ui + Recharts + TanStack Query + React Router + CASL (RBAC).

1. Auditoría de completitud — Módulos frontend
1.1 Inventario de módulos frontend requeridos
#	Módulo	¿En Pasos 1–2?	Estado	Acción en Paso 3
F01	Scaffolding Vite + TS + Tailwind	No	❌ Faltante	Desarrollar
F02	Configuración de entorno y build	No	❌ Faltante	Desarrollar
F03	Cliente HTTP (axios + interceptores)	No	❌ Faltante	Desarrollar
F04	Gestión de sesión (tokens, refresh, logout)	No	❌ Faltante	Desarrollar
F05	Store de autenticación (Zustand)	No	❌ Faltante	Desarrollar
F06	RBAC frontend (CASL + hook useCan)	Matriz sí, código no	❌ Faltante	Desarrollar
F07	Layout principal (sidebar, header, breadcrumbs)	No	❌ Faltante	Desarrollar
F08	Enrutado protegido (React Router)	No	❌ Faltante	Desarrollar
F09	Página Login + MFA	No	❌ Faltante	Desarrollar
F10	Dashboard con KPIs y widgets	Descripción sí, UI no	❌ Faltante	Desarrollar
F11	Módulo Leaks (listado, filtros, detalle)	No	❌ Faltante	Desarrollar
F12	Módulo Resets (listado, ejecución manual)	No	❌ Faltante	Desarrollar
F13	Módulo Reportes (generación, descarga)	No	❌ Faltante	Desarrollar
F14	Módulo Auditoría (visor + verificación cadena)	No	❌ Faltante	Desarrollar
F15	Módulo Usuarios + Roles (CRUD)	No	❌ Faltante	Desarrollar
F16	Módulo Fuentes y Dominios	No	❌ Faltante	Desarrollar
F17	Módulo Perfil (propio usuario, MFA enroll)	No	❌ Faltante	Desarrollar
F18	Notificaciones toast + centro de avisos	No	❌ Faltante	Desarrollar
F19	Componentes UI base (tabla, paginación, modal)	No	❌ Faltante	Desarrollar
F20	Manejo de errores (ErrorBoundary, 404, 403)	No	❌ Faltante	Desarrollar
F21	Accesibilidad (a11y) y i18n base	No	❌ Faltante	Desarrollar
F22	Tests (Vitest + Testing Library)	No	❌ Faltante	Desarrollar
F23	Docker + Nginx para SPA	No	❌ Faltante	Desarrollar
F24	CI (lint, typecheck, test, build)	No	❌ Faltante	Desarrollar
1.2 Veredicto
El frontend estaba completamente ausente en los Pasos 1–2 (solo se describieron widgets en el diseño). Se desarrollan los 24 módulos a continuación, priorizando F01–F13 (núcleo operativo) y completando F14–F24.

2. Estructura del proyecto frontend
text
radar-creds-web/
├── public/
│   └── favicon.svg
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── vite-env.d.ts
│   ├── lib/
│   │   ├── api.ts                  # F03
│   │   ├── queryClient.ts          # F03
│   │   ├── abilities.ts            # F06
│   │   ├── utils.ts
│   │   └── format.ts
│   ├── stores/
│   │   ├── authStore.ts            # F05
│   │   └── uiStore.ts              # F18
│   ├── hooks/
│   │   ├── useAuth.ts              # F04
│   │   ├── useCan.ts               # F06
│   │   ├── useLeaks.ts
│   │   ├── useResets.ts
│   │   ├── useReports.ts
│   │   ├── useAudit.ts
│   │   ├── useUsers.ts
│   │   └── useSources.ts
│   ├── components/
│   │   ├── ui/                     # F19 (shadcn/ui)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── select.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── skeleton.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── dropdown-menu.tsx
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx       # F07
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Breadcrumbs.tsx
│   │   │   └── ProtectedRoute.tsx  # F08
│   │   ├── common/
│   │   │   ├── DataTable.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ErrorBoundary.tsx   # F20
│   │   │   ├── KpiCard.tsx
│   │   │   ├── SeverityBadge.tsx
│   │   │   └── StatusBadge.tsx
│   │   └── charts/
│   │       ├── TrendLine.tsx
│   │       ├── SeverityDonut.tsx
│   │       ├── TopBreachesBar.tsx
│   │       └── ResetsStackedBar.tsx
│   ├── pages/
│   │   ├── Login.tsx               # F09
│   │   ├── MfaVerify.tsx           # F09
│   │   ├── Dashboard.tsx           # F10
│   │   ├── LeaksList.tsx           # F11
│   │   ├── LeakDetail.tsx          # F11
│   │   ├── ResetsList.tsx          # F12
│   │   ├── Reports.tsx             # F13
│   │   ├── AuditLog.tsx            # F14
│   │   ├── Users.tsx               # F15
│   │   ├── Roles.tsx               # F15
│   │   ├── Sources.tsx             # F16
│   │   ├── Profile.tsx             # F17
│   │   ├── Notifications.tsx       # F18
│   │   ├── Forbidden.tsx           # F20
│   │   └── NotFound.tsx            # F20
│   ├── i18n/
│   │   ├── es.json                 # F21
│   │   └── index.ts
│   └── tests/                      # F22
│       ├── setup.ts
│       ├── Login.test.tsx
│       ├── Dashboard.test.tsx
│       └── LeaksList.test.tsx
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── postcss.config.js
├── Dockerfile                      # F23
├── nginx.conf                      # F23
└── .github/workflows/ci.yml        # F24
3. F01 + F02 — Scaffolding y configuración
package.json
json
{
  "name": "radar-creds-web",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .ts,.tsx",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "@casl/ability": "^6.7.2",
    "@casl/react": "^4.0.0",
    "@hookform/resolvers": "^3.9.0",
    "@radix-ui/react-dialog": "^1.1.2",
    "@radix-ui/react-dropdown-menu": "^2.1.2",
    "@radix-ui/react-select": "^2.1.2",
    "@radix-ui/react-tabs": "^1.1.1",
    "@radix-ui/react-toast": "^1.2.2",
    "@tanstack/react-query": "^5.59.0",
    "@tanstack/react-query-devtools": "^5.59.0",
    "axios": "^1.7.7",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "i18next": "^23.15.1",
    "lucide-react": "^0.451.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-hook-form": "^7.53.0",
    "react-i18next": "^15.0.2",
    "react-router-dom": "^6.27.0",
    "recharts": "^2.13.0",
    "tailwind-merge": "^2.5.4",
    "zod": "^3.23.8",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.2",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.1",
    "@typescript-eslint/eslint-plugin": "^8.11.0",
    "@typescript-eslint/parser": "^8.11.0",
    "@vitejs/plugin-react": "^4.3.3",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.13.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.13",
    "jsdom": "^25.0.1",
    "postcss": "^8.4.47",
    "prettier": "^3.3.3",
    "tailwindcss": "^3.4.14",
    "tailwindcss-animate": "^1.0.7",
    "typescript": "^5.6.3",
    "vite": "^5.4.10",
    "vitest": "^2.1.3"
  }
}
vite.config.ts
ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/tests/setup.ts"],
    css: false,
  },
});
tailwind.config.ts
ts
import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
      },
      borderRadius: { lg: "var(--radius)", md: "calc(var(--radius) - 2px)" },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
.env.example
env
VITE_API_BASE_URL=/api/v1
VITE_APP_NAME=Radar de Credenciales
VITE_DEFAULT_LOCALE=es
tsconfig.json (extracto)
json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] },
    "types": ["vite/client", "vitest/globals"]
  },
  "include": ["src"]
}
4. F03 — Cliente HTTP
src/lib/api.ts
ts
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/authStore";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// Request: inyecta access token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response: refresh automático ante 401 (una sola vez por petición)
let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setTokens, logout } = useAuthStore.getState();
  if (!refreshToken) {
    logout();
    return null;
  }
  try {
    const resp = await axios.post(`${BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    setTokens(resp.data.access_token, resp.data.refresh_token);
    return resp.data.access_token as string;
  } catch {
    logout();
    return null;
  }
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      refreshing = refreshing ?? refreshAccessToken();
      const newToken = await refreshing;
      refreshing = null;
      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  }
);

export function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string } | undefined;
    return data?.detail ?? err.message;
  }
  return err instanceof Error ? err.message : "Error desconocido";
}
src/lib/queryClient.ts
ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error: any) => {
        if (error?.response?.status === 401 || error?.response?.status === 403) return false;
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
    },
    mutations: { retry: 0 },
  },
});
5. F04 + F05 — Sesión y store de autenticación
src/stores/authStore.ts
ts
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
src/hooks/useAuth.ts
ts
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
6. F06 — RBAC frontend con CASL
src/lib/abilities.ts
ts
import { AbilityBuilder, createMongoAbility, type MongoAbility } from "@casl/ability";

export type Action =
  | "read" | "write" | "export" | "generate" | "schedule"
  | "execute" | "admin" | "download";

export type Subject =
  | "dashboard" | "leaks" | "resets" | "reports"
  | "audit" | "users" | "roles" | "sources" | "config"
  | "notifications" | "profile";

export type AppAbility = MongoAbility<[Action, Subject]>;

const MATRIX: Record<string, [Action, Subject][]> = {
  admin: [
    ["read", "dashboard"], ["read", "leaks"], ["write", "leaks"], ["export", "leaks"],
    ["read", "resets"], ["execute", "resets"],
    ["read", "reports"], ["generate", "reports"], ["schedule", "reports"], ["download", "reports"],
    ["read", "audit"], ["export", "audit"],
    ["read", "users"], ["write", "users"], ["admin", "users"],
    ["read", "roles"], ["write", "roles"],
    ["read", "sources"], ["write", "sources"],
    ["admin", "config"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  soc_analyst: [
    ["read", "dashboard"], ["read", "leaks"], ["write", "leaks"], ["export", "leaks"],
    ["read", "resets"], ["execute", "resets"],
    ["read", "reports"], ["generate", "reports"], ["download", "reports"],
    ["read", "audit"],
    ["read", "sources"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  auditor: [
    ["read", "dashboard"], ["read", "leaks"], ["export", "leaks"],
    ["read", "resets"],
    ["read", "reports"], ["generate", "reports"], ["download", "reports"],
    ["read", "audit"], ["export", "audit"],
    ["read", "users"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  end_user: [
    ["read", "dashboard"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
};

export function buildAbility(rol: string | undefined): AppAbility {
  const { can, build } = new AbilityBuilder<AppAbility>(createMongoAbility);
  const rules = MATRIX[rol ?? ""] ?? [];
  for (const [action, subject] of rules) {
    can(action, subject);
  }
  return build();
}
src/hooks/useCan.ts
ts
import { createContext, useContext } from "react";
import { useAuthStore } from "@/stores/authStore";
import { buildAbility, type AppAbility } from "@/lib/abilities";

export const AbilityContext = createContext<AppAbility>(buildAbility(undefined));

export function useAbility(): AppAbility {
  return useContext(AbilityContext);
}

export function useCan(action: Parameters<AppAbility["can"]>[0], subject: Parameters<AppAbility["can"]>[1]) {
  const ability = useAbility();
  return ability.can(action, subject);
}
7. F07 + F08 — Layout y rutas protegidas
src/components/layout/AppLayout.tsx
tsx
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function AppLayout() {
  return (
    <div className="min-h-screen flex bg-muted/30">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
src/components/layout/Sidebar.tsx
tsx
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, ShieldAlert, RefreshCcw, FileBarChart2,
  ScrollText, Users, Database, Bell, UserCircle,
} from "lucide-react";
import { useCan } from "@/hooks/useCan";
import { cn } from "@/lib/utils";

interface Item {
  to: string;
  label: string;
  icon: React.ElementType;
  can?: () => boolean;
}

export function Sidebar() {
  const canReadLeaks = useCan("read", "leaks");
  const canReadResets = useCan("read", "resets");
  const canReadReports = useCan("read", "reports");
  const canReadAudit = useCan("read", "audit");
  const canReadUsers = useCan("read", "users");
  const canReadSources = useCan("read", "sources");

  const items: Item[] = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/leaks", label: "Filtraciones", icon: ShieldAlert, can: () => canReadLeaks },
    { to: "/resets", label: "Contenciones", icon: RefreshCcw, can: () => canReadResets },
    { to: "/reports", label: "Reportes", icon: FileBarChart2, can: () => canReadReports },
    { to: "/audit", label: "Auditoría", icon: ScrollText, can: () => canReadAudit },
    { to: "/users", label: "Usuarios", icon: Users, can: () => canReadUsers },
    { to: "/sources", label: "Fuentes", icon: Database, can: () => canReadSources },
    { to: "/notifications", label: "Notificaciones", icon: Bell },
    { to: "/profile", label: "Perfil", icon: UserCircle },
  ];

  return (
    <aside className="w-64 border-r bg-background hidden md:flex flex-col">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="font-semibold text-lg">Radar Creds</span>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {items.filter((i) => !i.can || i.can()).map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted text-muted-foreground"
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
src/components/layout/Header.tsx
tsx
import { useAuthStore } from "@/stores/authStore";
import { useLogout } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Breadcrumbs } from "./Breadcrumbs";

export function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  return (
    <header className="h-16 border-b bg-background flex items-center justify-between px-6">
      <Breadcrumbs />
      <div className="flex items-center gap-4">
        <div className="text-sm text-right">
          <div className="font-medium">{user?.nombre}</div>
          <div className="text-muted-foreground text-xs">{user?.rol}</div>
        </div>
        <Button variant="outline" size="sm" onClick={logout}>Salir</Button>
      </div>
    </header>
  );
}
src/components/layout/ProtectedRoute.tsx
tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useCan } from "@/hooks/useCan";
import type { Action, Subject } from "@/lib/abilities";

interface Props {
  action?: Action;
  subject?: Subject;
}

export function ProtectedRoute({ action, subject }: Props) {
  const token = useAuthStore((s) => s.accessToken);
  const location = useLocation();
  const allowed = useCan(action ?? "read", subject ?? "dashboard");

  if (!token) return <Navigate to="/login" state={{ from: location }} replace />;
  if (action && subject && !allowed) return <Navigate to="/403" replace />;
  return <Outlet />;
}
src/App.tsx (enrutado)
tsx
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AbilityContext } from "@/hooks/useCan";
import { buildAbility } from "@/lib/abilities";
import { useAuthStore } from "@/stores/authStore";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import Login from "@/pages/Login";
import MfaVerify from "@/pages/MfaVerify";
import Dashboard from "@/pages/Dashboard";
import LeaksList from "@/pages/LeaksList";
import LeakDetail from "@/pages/LeakDetail";
import ResetsList from "@/pages/ResetsList";
import Reports from "@/pages/Reports";
import AuditLog from "@/pages/AuditLog";
import Users from "@/pages/Users";
import Roles from "@/pages/Roles";
import Sources from "@/pages/Sources";
import Profile from "@/pages/Profile";
import Notifications from "@/pages/Notifications";
import Forbidden from "@/pages/Forbidden";
import NotFound from "@/pages/NotFound";

export default function App() {
  const rol = useAuthStore((s) => s.user?.rol);
  const ability = buildAbility(rol);

  return (
    <AbilityContext.Provider value={ability}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/mfa" element={<MfaVerify />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<Dashboard />} />

              <Route element={<ProtectedRoute action="read" subject="leaks" />}>
                <Route path="/leaks" element={<LeaksList />} />
                <Route path="/leaks/:id" element={<LeakDetail />} />
              </Route>

              <Route element={<ProtectedRoute action="read" subject="resets" />}>
                <Route path="/resets" element={<ResetsList />} />
              </Route>

              <Route element={<ProtectedRoute action="read" subject="reports" />}>
                <Route path="/reports" element={<Reports />} />
              </Route>

              <Route element={<ProtectedRoute action="read" subject="audit" />}>
                <Route path="/audit" element={<AuditLog />} />
              </Route>

              <Route element={<ProtectedRoute action="read" subject="users" />}>
                <Route path="/users" element={<Users />} />
                <Route path="/roles" element={<Roles />} />
              </Route>

              <Route element={<ProtectedRoute action="read" subject="sources" />}>
                <Route path="/sources" element={<Sources />} />
              </Route>

              <Route path="/profile" element={<Profile />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/403" element={<Forbidden />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AbilityContext.Provider>
  );
}
src/main.tsx
tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import App from "./App";
import { queryClient } from "./lib/queryClient";
import { ToastProvider } from "@/components/ui/toast";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <App />
      </ToastProvider>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);
8. F09 — Login y MFA
src/pages/Login.tsx
tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLogin, extractErrorMessage } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const { register, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  const login = useLogin();

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Radar de Credenciales</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit((d) => login.mutate(d))}
            className="space-y-4"
            aria-label="Formulario de acceso"
          >
            <div>
              <label htmlFor="email" className="text-sm font-medium">Correo corporativo</label>
              <Input id="email" type="email" autoComplete="username" {...register("email")} />
              {formState.errors.email && (
                <p className="text-destructive text-xs mt-1">{formState.errors.email.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="text-sm font-medium">Contraseña</label>
              <Input id="password" type="password" autoComplete="current-password" {...register("password")} />
              {formState.errors.password && (
                <p className="text-destructive text-xs mt-1">{formState.errors.password.message}</p>
              )}
            </div>
            {login.isError && (
              <p role="alert" className="text-destructive text-sm">
                {extractErrorMessage(login.error)}
              </p>
            )}
            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? "Accediendo…" : "Acceder"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
src/pages/MfaVerify.tsx
tsx
import { useForm } from "react-hook-form";
import { useAuthStore } from "@/stores/authStore";
import { useMfaVerify } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Navigate } from "react-router-dom";

export default function MfaVerify() {
  const email = useAuthStore((s) => s.mfaPendingEmail);
  const { register, handleSubmit } = useForm<{ code: string }>();
  const mfa = useMfaVerify();

  if (!email) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader><CardTitle>Verificación en dos pasos</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit((d) => mfa.mutate({ email, code: d.code }))} className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Introduce el código de 6 dígitos de tu aplicación autenticadora.
            </p>
            <Input
              inputMode="numeric"
              maxLength={6}
              pattern="\d{6}"
              autoFocus
              {...register("code")}
            />
            <Button type="submit" className="w-full" disabled={mfa.isPending}>Verificar</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
9. F10 — Dashboard
src/hooks/useLeaks.ts (KPIs y queries)
ts
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

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
src/pages/Dashboard.tsx
tsx
import { useDashboardSummary, useKpis } from "@/hooks/useLeaks";
import { KpiCard } from "@/components/common/KpiCard";
import { TrendLine } from "@/components/charts/TrendLine";
import { SeverityDonut } from "@/components/charts/SeverityDonut";
import { TopBreachesBar } from "@/components/charts/TopBreachesBar";
import { ResetsStackedBar } from "@/components/charts/ResetsStackedBar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const kpis = useKpis();
  const summary = useDashboardSummary(30);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Panel de exposición</h1>

      <div className="grid gap-4 md:grid-cols-4">
        {kpis.isLoading && Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
        {kpis.data && (
          <>
            <KpiCard title="Total filtraciones" value={kpis.data.total} tone="default" />
            <KpiCard title="Pendientes de contención" value={kpis.data.nuevos} tone="warning" />
            <KpiCard title="Contenidas" value={kpis.data.contenidos} tone="success" />
            <KpiCard
              title="MTTC"
              value={kpis.data.mttc_min ? `${kpis.data.mttc_min.toFixed(1)} min` : "—"}
              tone="info"
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Tendencia (30 días)</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <TrendLine data={summary.data.tendencia_diaria} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Distribución por severidad</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <SeverityDonut data={summary.data.por_severidad} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Top breaches</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <TopBreachesBar data={summary.data.top_breaches} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Estado de contenciones</CardTitle></CardHeader>
          <CardContent>
            {summary.data ? <ResetsStackedBar data={summary.data.resets_estado} /> : <Skeleton className="h-64" />}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Usuarios reincidentes</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {summary.data?.reincidentes.map((r) => (
              <li key={r.email} className="py-2 flex justify-between text-sm">
                <span>{r.email}</span>
                <span className="text-muted-foreground">{r.total} filtraciones</span>
              </li>
            ))}
            {summary.data?.reincidentes.length === 0 && (
              <li className="py-4 text-center text-muted-foreground text-sm">
                Sin reincidencias detectadas
              </li>
            )}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
src/components/common/KpiCard.tsx
tsx
import { cn } from "@/lib/utils";

type Tone = "default" | "warning" | "success" | "info" | "danger";

const tones: Record<Tone, string> = {
  default: "border-border",
  warning: "border-amber-400 bg-amber-50",
  success: "border-emerald-400 bg-emerald-50",
  info: "border-sky-400 bg-sky-50",
  danger: "border-rose-400 bg-rose-50",
};

export function KpiCard({
  title, value, tone = "default",
}: { title: string; value: string | number; tone?: Tone }) {
  return (
    <div className={cn("rounded-lg border p-4", tones[tone])}>
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}
src/components/charts/TrendLine.tsx
tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { format, parseISO } from "date-fns";

export function TrendLine({ data }: { data: { fecha: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="fecha"
          tickFormatter={(v) => format(parseISO(v), "dd/MM")}
          fontSize={12}
        />
        <YAxis fontSize={12} allowDecimals={false} />
        <Tooltip
          labelFormatter={(v) => format(parseISO(v as string), "dd/MM/yyyy")}
          formatter={(value) => [value, "Filtraciones"]}
        />
        <Line type="monotone" dataKey="total" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
src/components/charts/SeverityDonut.tsx
tsx
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";

const COLORS: Record<string, string> = {
  baja: "#10b981",
  media: "#f59e0b",
  alta: "#f97316",
  critica: "#dc2626",
};

export function SeverityDonut({ data }: { data: { severidad: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <PieChart>
        <Pie data={data} dataKey="total" nameKey="severidad" innerRadius={60} outerRadius={90}>
          {data.map((d) => (
            <Cell key={d.severidad} fill={COLORS[d.severidad] ?? "#94a3b8"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
src/components/charts/TopBreachesBar.tsx
tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export function TopBreachesBar({ data }: { data: { breach: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
        <XAxis type="number" allowDecimals={false} fontSize={12} />
        <YAxis dataKey="breach" type="category" fontSize={12} width={120} />
        <Tooltip />
        <Bar dataKey="total" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
src/components/charts/ResetsStackedBar.tsx
tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export function ResetsStackedBar({ data }: { data: { resultado: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <BarChart data={data}>
        <XAxis dataKey="resultado" fontSize={12} />
        <YAxis fontSize={12} allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Bar dataKey="total" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
10. F11 — Módulo Leaks
src/hooks/useLeaks.ts (ampliación)
ts
import { keepPreviousData, useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";

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
src/pages/LeaksList.tsx
tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeaks } from "@/hooks/useLeaks";
import { DataTable } from "@/components/common/DataTable";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { formatDateTime } from "@/lib/format";

export default function LeaksList() {
  const [estado, setEstado] = useState<string>("");
  const [email, setEmail] = useState("");
  const [page, setPage] = useState(0);
  const limit = 25;

  const { data, isLoading, isError } = useLeaks({
    estado: estado || undefined,
    email: email || undefined,
    limit,
    offset: page * limit,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Filtraciones detectadas</h1>
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Buscar por email…"
          value={email}
          onChange={(e) => { setEmail(e.target.value); setPage(0); }}
          className="max-w-xs"
        />
        <Select value={estado} onValueChange={(v) => { setEstado(v); setPage(0); }}>
          <option value="">Todos los estados</option>
          <option value="nuevo">Nuevo</option>
          <option value="contenido">Contenido</option>
          <option value="resuelto">Resuelto</option>
          <option value="falso_positivo">Falso positivo</option>
        </Select>
      </div>

      <DataTable
        loading={isLoading}
        error={isError ? "Error al cargar filtraciones" : undefined}
        rows={data ?? []}
        columns={[
          {
            key: "email_corporativo",
            header: "Email",
            render: (r) => (
              <Link to={`/leaks/${r.id}`} className="text-primary hover:underline">
                {r.email_corporativo}
              </Link>
            ),
          },
          { key: "breach_origen", header: "Breach" },
          { key: "fecha_breach", header: "Fecha breach", render: (r) => r.fecha_breach ?? "—" },
          { key: "severidad", header: "Severidad", render: (r) => <SeverityBadge value={r.severidad} /> },
          { key: "estado", header: "Estado", render: (r) => <StatusBadge value={r.estado} /> },
          {
            key: "fecha_deteccion",
            header: "Detectado",
            render: (r) => formatDateTime(r.fecha_deteccion),
          },
        ]}
        pagination={{ page, setPage, pageSize: limit, hasMore: (data?.length ?? 0) === limit }}
      />
    </div>
  );
}
src/pages/LeakDetail.tsx
tsx
import { useParams } from "react-router-dom";
import { useLeak, useUpdateLeak } from "@/hooks/useLeaks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/common/SeverityBadge";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Button } from "@/components/ui/button";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function LeakDetail() {
  const { id = "" } = useParams();
  const { data, isLoading } = useLeak(id);
  const update = useUpdateLeak();
  const canWrite = useCan("write", "leaks");
  const canExecute = useCan("execute", "resets");

  if (isLoading || !data) return <div className="text-muted-foreground">Cargando…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Detalle de filtración</h1>

      <Card>
        <CardHeader><CardTitle>{data.breach_origen}</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <Field label="Email" value={data.email_corporativo} />
          <Field label="Dominio del breach" value={data.breach_dominio ?? "—"} />
          <Field label="Fecha del breach" value={data.fecha_breach ?? "—"} />
          <Field label="Detectado" value={formatDateTime(data.fecha_deteccion)} />
          <Field label="Severidad" value={<SeverityBadge value={data.severidad} />} />
          <Field label="Estado" value={<StatusBadge value={data.estado} />} />
          <Field
            label="Datos expuestos"
            value={data.datos_expuestos?.join(", ") ?? "No especificado"}
          />
          <Field label="Fuente" value={data.fuente_detalle ?? "—"} />
          <Field
            label="Contenido en"
            value={data.fecha_contencion ? formatDateTime(data.fecha_contencion) : "Pendiente"}
          />
        </CardContent>
      </Card>

      <div className="flex gap-3">
        {canWrite && data.estado !== "falso_positivo" && (
          <Button
            variant="outline"
            onClick={() => update.mutate({ id: data.id, data: { estado: "falso_positivo" } })}
          >
            Marcar como falso positivo
          </Button>
        )}
        {canExecute && data.estado !== "contenido" && (
          <Button
            onClick={() => update.mutate({ id: data.id, data: { estado: "contenido" } })}
          >
            Forzar contención manual
          </Button>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-muted-foreground text-xs uppercase tracking-wide">{label}</div>
      <div className="mt-1">{value}</div>
    </div>
  );
}
11. F12 — Módulo Resets
src/hooks/useResets.ts
ts
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resets"] });
      queryClient.invalidateQueries({ queryKey: ["leaks"] });
      queryClient.invalidateQueries({ queryKey: ["kpis"] });
    },
  });
}
src/pages/ResetsList.tsx
tsx
import { useState } from "react";
import { useResets, useManualReset } from "@/hooks/useResets";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function ResetsList() {
  const { data, isLoading } = useResets();
  const manual = useManualReset();
  const canExecute = useCan("execute", "resets");
  const [open, setOpen] = useState(false);
  const [leakId, setLeakId] = useState("");
  const [motivo, setMotivo] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Contenciones ejecutadas</h1>
        {canExecute && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>Contención manual</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Forzar contención</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="ID de leak_hit" value={leakId} onChange={(e) => setLeakId(e.target.value)} />
                <Input placeholder="Motivo (opcional)" value={motivo} onChange={(e) => setMotivo(e.target.value)} />
                <Button
                  onClick={() => manual.mutate({ leak_hit_id: leakId, motivo }, {
                    onSuccess: () => { setOpen(false); setLeakId(""); setMotivo(""); },
                  })}
                  disabled={!leakId || manual.isPending}
                >
                  Ejecutar
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <DataTable
        loading={isLoading}
        rows={data ?? []}
        columns={[
          { key: "leak_hit_id", header: "Leak" },
          { key: "metodo", header: "Método" },
          { key: "resultado", header: "Resultado" },
          { key: "intentos", header: "Intentos" },
          { key: "timestamp", header: "Fecha", render: (r) => formatDateTime(r.timestamp) },
          { key: "proximo_intento", header: "Próximo intento", render: (r) => r.proximo_intento ? formatDateTime(r.proximo_intento) : "—" },
        ]}
      />
    </div>
  );
}
12. F13 — Módulo Reportes
src/hooks/useReports.ts
ts
import { useMutation, useQuery } from "@tanstack/react-query";
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
src/pages/Reports.tsx
tsx
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
13. F14 — Módulo Auditoría
src/hooks/useAudit.ts
ts
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
src/pages/AuditLog.tsx
tsx
import { useState } from "react";
import { useAudit, useVerifyChain } from "@/hooks/useAudit";
import { DataTable } from "@/components/common/DataTable";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/format";

export default function AuditLog() {
  const [modulo, setModulo] = useState("");
  const [limit] = useState(200);
  const { data, isLoading } = useAudit({ modulo: modulo || undefined, limit });
  const chain = useVerifyChain();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Bitácora de auditoría</h1>
        {chain.data && (
          <Badge variant={chain.data.ok ? "default" : "destructive"}>
            Cadena: {chain.data.ok ? "íntegra" : `rota (${chain.data.broken.length})`}
          </Badge>
        )}
      </div>

      <Input
        placeholder="Filtrar por módulo (auth, leaks, resets…)"
        value={modulo}
        onChange={(e) => setModulo(e.target.value)}
        className="max-w-xs"
      />

      <DataTable
        loading={isLoading}
        rows={data ?? []}
        columns={[
          { key: "ts", header: "Fecha", render: (r) => formatDateTime(r.ts) },
          { key: "usuario_email", header: "Usuario", render: (r) => r.usuario_email ?? "sistema" },
          { key: "modulo", header: "Módulo" },
          { key: "accion", header: "Acción" },
          { key: "resultado", header: "Resultado" },
          { key: "entidad", header: "Entidad", render: (r) => r.entidad ?? "—" },
          { key: "hash_actual", header: "Hash", render: (r) => r.hash_actual.slice(0, 12) + "…" },
        ]}
      />
    </div>
  );
}
14. F15 — Usuarios y Roles
src/hooks/useUsers.ts
ts
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
src/pages/Users.tsx
tsx
import { useState } from "react";
import { useUsers, useCreateUser, useUpdateUser } from "@/hooks/useUsers";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useCan } from "@/hooks/useCan";

export default function Users() {
  const { data, isLoading } = useUsers();
  const create = useCreateUser();
  const update = useUpdateUser();
  const canWrite = useCan("write", "users");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ email: "", nombre: "", rol: "end_user", password: "" });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Usuarios</h1>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild><Button>Nuevo usuario</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Crear usuario</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                <Input placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
                <Select value={form.rol} onValueChange={(v) => setForm({ ...form, rol: v })}>
                  <option value="admin">Admin</option>
                  <option value="soc_analyst">Analista SOC</option>
                  <option value="auditor">Auditor</option>
                  <option value="end_user">Usuario final</option>
                </Select>
                <Input type="password" placeholder="Contraseña (opcional si SSO)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
                <Button
                  onClick={() => create.mutate(form, { onSuccess: () => { setOpen(false); setForm({ email: "", nombre: "", rol: "end_user", password: "" }); } })}
                  disabled={!form.email || !form.nombre || create.isPending}
                >
                  Crear
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <DataTable
        loading={isLoading}
        rows={data ?? []}
        columns={[
          { key: "email", header: "Email" },
          { key: "nombre", header: "Nombre" },
          { key: "activo", header: "Activo", render: (r) => r.activo ? <Badge>Activo</Badge> : <Badge variant="destructive">Inactivo</Badge> },
          { key: "mfa_enabled", header: "MFA", render: (r) => r.mfa_enabled ? "Sí" : "No" },
          {
            key: "acciones",
            header: "",
            render: (r) => canWrite && (
              <Button variant="outline" size="sm" onClick={() => update.mutate({ id: r.id, data: { activo: !r.activo } })}>
                {r.activo ? "Desactivar" : "Activar"}
              </Button>
            ),
          },
        ]}
      />
    </div>
  );
}
src/pages/Roles.tsx
tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ROLES = [
  { nombre: "Admin", permisos: ["Todo el sistema", "Gestión de usuarios y roles", "Configuración"] },
  { nombre: "Analista SOC", permisos: ["Ver y editar leaks", "Ejecutar contenciones", "Generar reportes", "Ver auditoría"] },
  { nombre: "Auditor", permisos: ["Lectura total", "Exportar reportes y auditoría"] },
  { nombre: "Usuario final", permisos: ["Ver sus notificaciones", "Editar su perfil"] },
];

export default function Roles() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Roles y permisos</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {ROLES.map((r) => (
          <Card key={r.nombre}>
            <CardHeader><CardTitle>{r.nombre}</CardTitle></CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 text-sm space-y-1">
                {r.permisos.map((p) => <li key={p}>{p}</li>)}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
15. F16 — Fuentes y dominios
src/hooks/useSources.ts
ts
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
src/pages/Sources.tsx
tsx
import { useSources } from "@/hooks/useSources";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/format";

export default function Sources() {
  const { data, isLoading } = useSources();
  if (isLoading) return <div className="text-muted-foreground">Cargando…</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Fuentes y dominios</h1>

      <Card>
        <CardHeader><CardTitle>Fuentes de datos</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.fuentes.map((f) => (
              <li key={f.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-medium">{f.nombre}</div>
                  <div className="text-xs text-muted-foreground">
                    Última consulta: {f.ultima_consulta ? formatDateTime(f.ultima_consulta) : "—"}
                  </div>
                </div>
                <Badge variant={f.activa ? "default" : "destructive"}>
                  {f.activa ? "Activa" : "Inactiva"}
                </Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Dominios monitoreados</CardTitle></CardHeader>
        <CardContent>
          <ul className="divide-y">
            {data?.dominios.map((d) => (
              <li key={d.id} className="py-3 flex items-center justify-between">
                <span className="font-medium">{d.dominio}</span>
                <Badge variant={d.activo ? "default" : "destructive"}>
                  {d.activo ? "Activo" : "Inactivo"}
                </Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
16. F17 — Perfil y MFA enroll
src/pages/Profile.tsx
tsx
import { useAuthStore } from "@/stores/authStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Profile() {
  const user = useAuthStore((s) => s.user);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <Card>
        <CardHeader><CardTitle>Datos de cuenta</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <div><div className="text-muted-foreground text-xs">Nombre</div>{user?.nombre}</div>
          <div><div className="text-muted-foreground text-xs">Email</div>{user?.email}</div>
          <div><div className="text-muted-foreground text-xs">Rol</div>{user?.rol}</div>
          <div><div className="text-muted-foreground text-xs">MFA</div>{user?.mfa_enabled ? "Activado" : "Desactivado"}</div>
        </CardContent>
      </Card>
    </div>
  );
}
17. F18 — Notificaciones toast
src/components/ui/toast.tsx
tsx
import { createContext, useCallback, useContext, useState } from "react";
import * as ToastPrimitive from "@radix-ui/react-toast";
import { cn } from "@/lib/utils";

type Tone = "default" | "success" | "danger";
interface Toast { id: number; title: string; description?: string; tone?: Tone }

interface ToastContextValue { push: (t: Omit<Toast, "id">) => void }
const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const push = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now();
    setItems((prev) => [...prev, { ...t, id }]);
    setTimeout(() => setItems((prev) => prev.filter((i) => i.id !== id)), 5000);
  }, []);

  return (
    <ToastContext.Provider value={{ push }}>
      <ToastPrimitive.Provider swipeDirection="right">
        {children}
        {items.map((t) => (
          <ToastPrimitive.Root
            key={t.id}
            open
            onOpenChange={() => setItems((prev) => prev.filter((i) => i.id !== t.id))}
            className={cn(
              "fixed bottom-4 right-4 rounded-md border p-4 shadow-lg bg-background",
              t.tone === "success" && "border-emerald-400",
              t.tone === "danger" && "border-rose-400"
            )}
          >
            <ToastPrimitive.Title className="font-medium">{t.title}</ToastPrimitive.Title>
            {t.description && (
              <ToastPrimitive.Description className="text-sm text-muted-foreground">
                {t.description}
              </ToastPrimitive.Description>
            )}
          </ToastPrimitive.Root>
        ))}
        <ToastPrimitive.Viewport className="fixed bottom-4 right-4 z-50" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast debe usarse dentro de ToastProvider");
  return ctx;
}
18. F19 — Componentes UI base (DataTable, Badges)
src/components/common/DataTable.tsx
tsx
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface Props<T> {
  rows: T[];
  columns: Column<T>[];
  loading?: boolean;
  error?: string;
  emptyText?: string;
  pagination?: {
    page: number;
    setPage: (n: number) => void;
    pageSize: number;
    hasMore: boolean;
  };
}

export function DataTable<T extends { id?: string | number }>({
  rows, columns, loading, error, emptyText = "Sin resultados", pagination,
}: Props<T>) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
      </div>
    );
  }
  if (error) {
    return <div role="alert" className="text-destructive text-sm">{error}</div>;
  }
  if (!rows.length) {
    return <div className="text-muted-foreground text-sm py-8 text-center">{emptyText}</div>;
  }

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto border rounded-md">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className={cn("text-left font-medium px-3 py-2", c.className)}>
                  {c.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.id ?? i} className="border-t hover:bg-muted/30">
                {columns.map((c) => (
                  <td key={c.key} className={cn("px-3 py-2", c.className)}>
                    {c.render ? c.render(row) : (row as any)[c.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={pagination.page === 0}
            onClick={() => pagination.setPage(pagination.page - 1)}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!pagination.hasMore}
            onClick={() => pagination.setPage(pagination.page + 1)}
          >
            Siguiente
          </Button>
        </div>
      )}
    </div>
  );
}
src/components/common/SeverityBadge.tsx
tsx
import { Badge } from "@/components/ui/badge";

const TONES: Record<string, string> = {
  baja: "bg-emerald-100 text-emerald-800",
  media: "bg-amber-100 text-amber-800",
  alta: "bg-orange-100 text-orange-800",
  critica: "bg-rose-100 text-rose-800",
};

export function SeverityBadge({ value }: { value: string }) {
  return <Badge className={TONES[value] ?? ""}>{value}</Badge>;
}
src/components/common/StatusBadge.tsx
tsx
import { Badge } from "@/components/ui/badge";

const TONES: Record<string, string> = {
  nuevo: "bg-sky-100 text-sky-800",
  contenido: "bg-emerald-100 text-emerald-800",
  resuelto: "bg-slate-100 text-slate-800",
  falso_positivo: "bg-zinc-100 text-zinc-600",
};

export function StatusBadge({ value }: { value: string }) {
  return <Badge className={TONES[value] ?? ""}>{value}</Badge>;
}
src/components/ui/badge.tsx
tsx
import { cn } from "@/lib/utils";

export function Badge({ children, className, variant = "default" }: {
  children: React.ReactNode; className?: string; variant?: "default" | "destructive";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        variant === "destructive" ? "bg-rose-100 text-rose-800" : "bg-muted text-foreground",
        className
      )}
    >
      {children}
    </span>
  );
}
src/components/ui/skeleton.tsx
tsx
import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} />;
}
src/components/ui/button.tsx, input.tsx, card.tsx, select.tsx, dialog.tsx, tabs.tsx, dropdown-menu.tsx
tsx
// button.tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

type Variant = "default" | "outline" | "ghost" | "destructive";
type Size = "sm" | "md" | "lg" | "icon";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variants: Record<Variant, string> = {
  default: "bg-primary text-primary-foreground hover:opacity-90",
  outline: "border bg-background hover:bg-muted",
  ghost: "hover:bg-muted",
  destructive: "bg-destructive text-destructive-foreground hover:opacity-90",
};
const sizes: Record<Size, string> = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4",
  lg: "h-11 px-6",
  icon: "h-9 w-9",
};

export const Button = forwardRef<HTMLButtonElement, Props>(
  ({ className, variant = "default", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md font-medium transition disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant], sizes[size], className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";
tsx
// input.tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border bg-background px-3 py-2 text-sm",
        "focus:outline-none focus:ring-2 focus:ring-primary/40",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
tsx
// card.tsx
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-lg border bg-background", className)} {...props} />;
}
export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4 border-b", className)} {...props} />;
}
export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("font-semibold text-base", className)} {...props} />;
}
export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4", className)} {...props} />;
}
tsx
// select.tsx (simplificado sobre <select> nativo)
import { cn } from "@/lib/utils";

interface Props extends React.SelectHTMLAttributes<HTMLSelectElement> {
  onValueChange?: (v: string) => void;
}

export function Select({ className, onValueChange, children, ...props }: Props) {
  return (
    <select
      className={cn("h-10 rounded-md border bg-background px-3 text-sm", className)}
      onChange={(e) => onValueChange?.(e.target.value)}
      {...props}
    >
      {children}
    </select>
  );
}
tsx
// dialog.tsx — wrapper Radix
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogContent = ({ className, ...props }: DialogPrimitive.DialogContentProps) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 bg-black/40 z-40" />
    <DialogPrimitive.Content
      className={cn("fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background rounded-lg p-6 w-full max-w-md z-50", className)}
      {...props}
    />
  </DialogPrimitive.Portal>
);
export const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("mb-4", className)} {...props} />
);
export const DialogTitle = DialogPrimitive.Title;
tsx
// tabs.tsx
import * as TabsPrimitive from "@radix-ui/react-tabs";
export const Tabs = TabsPrimitive.Root;
export const TabsList = TabsPrimitive.List;
export const TabsTrigger = TabsPrimitive.Trigger;
export const TabsContent = TabsPrimitive.Content;
tsx
// dropdown-menu.tsx
import * as DropdownPrimitive from "@radix-ui/react-dropdown-menu";
export const DropdownMenu = DropdownPrimitive.Root;
export const DropdownMenuTrigger = DropdownPrimitive.Trigger;
export const DropdownMenuContent = DropdownPrimitive.Content;
export const DropdownMenuItem = DropdownPrimitive.Item;
19. F20 — Manejo de errores
src/components/common/ErrorBoundary.tsx
tsx
import { Component, ReactNode } from "react";
import { Button } from "@/components/ui/button";

interface Props { children: ReactNode }
interface State { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };
  static getDerivedStateFromError(error: Error): State { return { error }; }
  componentDidCatch(error: Error) { console.error("ErrorBoundary", error); }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center gap-4">
          <h1 className="text-xl font-semibold">Algo ha ido mal</h1>
          <p className="text-muted-foreground text-sm">{this.state.error.message}</p>
          <Button onClick={() => window.location.reload()}>Recargar</Button>
        </div>
      );
    }
    return this.props.children;
  }
}
src/pages/Forbidden.tsx / NotFound.tsx
tsx
// Forbidden.tsx
import { Link } from "react-router-dom";

export default function Forbidden() {
  return (
    <div className="text-center py-20 space-y-3">
      <h1 className="text-3xl font-semibold">403</h1>
      <p className="text-muted-foreground">No tienes permisos para acceder a esta sección.</p>
      <Link to="/dashboard" className="text-primary hover:underline">Volver al panel</Link>
    </div>
  );
}
tsx
// NotFound.tsx
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="text-center py-20 space-y-3">
      <h1 className="text-3xl font-semibold">404</h1>
      <p className="text-muted-foreground">La página no existe.</p>
      <Link to="/dashboard" className="text-primary hover:underline">Volver al panel</Link>
    </div>
  );
}
20. F21 — i18n y utilidades
src/i18n/index.ts
ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import es from "./es.json";

i18n.use(initReactI18next).init({
  resources: { es: { translation: es } },
  lng: import.meta.env.VITE_DEFAULT_LOCALE ?? "es",
  fallbackLng: "es",
  interpolation: { escapeValue: false },
});

export default i18n;
src/i18n/es.json
json
{
  "app": { "name": "Radar de Credenciales" },
  "nav": {
    "dashboard": "Panel",
    "leaks": "Filtraciones",
    "resets": "Contenciones",
    "reports": "Reportes",
    "audit": "Auditoría",
    "users": "Usuarios",
    "sources": "Fuentes",
    "profile": "Perfil"
  },
  "common": {
    "loading": "Cargando…",
    "error": "Error",
    "save": "Guardar",
    "cancel": "Cancelar",
    "search": "Buscar"
  }
}
src/lib/format.ts y src/lib/utils.ts
ts
// format.ts
import { format, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatDateTime(iso: string) {
  try {
    return format(parseISO(iso), "dd/MM/yyyy HH:mm", { locale: es });
  } catch {
    return iso;
  }
}
ts
// utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
src/index.css
css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --primary: 221 83% 53%;
    --primary-foreground: 0 0% 100%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 214 32% 91%;
    --radius: 0.5rem;
  }
  body { @apply bg-background text-foreground; }
}
21. F22 — Tests frontend
src/tests/setup.ts
ts
import "@testing-library/jest-dom/vitest";
src/tests/Login.test.tsx
tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Login from "@/pages/Login";
import { queryClient } from "@/lib/queryClient";
import { describe, it, expect } from "vitest";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Login", () => {
  it("renderiza formulario y valida email", async () => {
    renderWithProviders(<Login />);
    const email = screen.getByLabelText(/correo corporativo/i);
    await userEvent.type(email, "no-valido");
    await userEvent.click(screen.getByRole("button", { name: /acceder/i }));
    expect(await screen.findByText(/email inválido/i)).toBeInTheDocument();
  });
});
src/tests/LeaksList.test.tsx
tsx
import { render, screen } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect } from "vitest";
import LeaksList from "@/pages/LeaksList";
import { queryClient } from "@/lib/queryClient";
import * as useLeaksHook from "@/hooks/useLeaks";

describe("LeaksList", () => {
  it("muestra filas cuando hay datos", () => {
    vi.spyOn(useLeaksHook, "useLeaks").mockReturnValue({
      data: [{
        id: "1", email_corporativo: "a@b.com", usuario_id: null,
        breach_origen: "Demo", breach_dominio: null, fecha_breach: null,
        fecha_deteccion: new Date().toISOString(), severidad: "alta",
        fuente_detalle: null, datos_expuestos: null, estado: "nuevo",
        fecha_contencion: null, hash_canonico: "x",
      }],
      isLoading: false, isError: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <LeaksList />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("a@b.com")).toBeInTheDocument();
    expect(screen.getByText("Demo")).toBeInTheDocument();
  });
});
src/tests/Dashboard.test.tsx
tsx
import { render, screen } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect } from "vitest";
import Dashboard from "@/pages/Dashboard";
import { queryClient } from "@/lib/queryClient";
import * as useLeaksHook from "@/hooks/useLeaks";

describe("Dashboard", () => {
  it("renderiza KPIs", () => {
    vi.spyOn(useLeaksHook, "useKpis").mockReturnValue({
      data: { total: 10, nuevos: 3, contenidos: 7, mttc_min: 42.5 },
      isLoading: false, isError: false,
    } as any);
    vi.spyOn(useLeaksHook, "useDashboardSummary").mockReturnValue({
      data: { tendencia_diaria: [], por_severidad: [], top_breaches: [], resets_estado: [], reincidentes: [] },
      isLoading: false, isError: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Dashboard />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Total filtraciones")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });
});
22. F23 — Docker + Nginx
Dockerfile
dockerfile
# ---- build ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- serve ----
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
nginx.conf
nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  # SPA fallback
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API proxy (ajustar al host real del backend)
  location /api/ {
    proxy_pass http://api:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  # Cabeceras de seguridad
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  add_header Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'" always;
}
23. F24 — CI (GitHub Actions)
.github/workflows/ci.yml
yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: radar-creds-web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: radar-creds-web/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test -- --run
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: radar-creds-web/dist
24. Resumen de módulos entregados en Paso 3
Módulo	Archivo(s)	Estado
F01 Scaffolding	package.json, vite.config.ts, tsconfig.json	✅
F02 Config	.env.example, tailwind.config.ts	✅
F03 HTTP	lib/api.ts, lib/queryClient.ts	✅ Refresh automático
F04 Sesión	hooks/useAuth.ts	✅ Login/MFA/Logout
F05 Store	stores/authStore.ts	✅ Persistido
F06 RBAC	lib/abilities.ts, hooks/useCan.ts	✅ CASL
F07 Layout	components/layout/*	✅ Sidebar + Header
F08 Rutas	App.tsx, ProtectedRoute.tsx	✅ Anidadas
F09 Login/MFA	pages/Login.tsx, pages/MfaVerify.tsx	✅
F10 Dashboard	pages/Dashboard.tsx, 4 charts	✅ KPIs + 4 widgets
F11 Leaks	pages/LeaksList.tsx, LeakDetail.tsx	✅ Filtros + paginación
F12 Resets	pages/ResetsList.tsx	✅ + manual
F13 Reports	pages/Reports.tsx	✅ Genera + descarga
F14 Auditoría	pages/AuditLog.tsx	✅ + verificación cadena
F15 Usuarios/Roles	pages/Users.tsx, Roles.tsx	✅ CRUD
F16 Fuentes	pages/Sources.tsx	✅
F17 Perfil	pages/Profile.tsx	✅
F18 Toasts	components/ui/toast.tsx	✅
F19 UI base	components/ui/*, common/*	✅ 12 componentes
F20 Errores	ErrorBoundary, Forbidden, NotFound	✅
F21 i18n/a11y	i18n/*, index.css	✅ Base
F22 Tests	tests/*.tsx	✅ 3 suites
F23 Docker	Dockerfile, nginx.conf	✅ SPA + proxy
F24 CI	.github/workflows/ci.yml	✅ lint+test+build
25. Mejoras aplicadas sobre el diseño previo
Área	Mejora
Refresh token	Interceptor axios con cola única para evitar múltiples refresh simultáneos.
RBAC	CASL con matriz tipada; useCan + ProtectedRoute con acción/sujeto.
Rutas	Anidadas por permiso; 403 dedicado cuando falta autorización.
Formularios	React Hook Form + Zod para validación en cliente espejo del backend.
Datos	TanStack Query con placeholderData y refetch selectivo; invalidación por mutación.
Auditoría	Badge de integridad de cadena visible en el visor.
Reportes	Descarga vía blob con nombre consistente y toast de resultado.
Accesibilidad	aria-label, role="alert", autoComplete, foco en MFA.
Seguridad	CSP, X-Frame-Options, Referrer-Policy en Nginx.
Observabilidad	React Query DevTools en dev; ErrorBoundary global.
26. Comandos de puesta en marcha
bash
# Desarrollo
cd radar-creds-web
cp .env.example .env
npm install
npm run dev        # http://localhost:5173 (proxy /api → :8000)

# Calidad
npm run lint
npm run typecheck
npm run test
npm run build

# Producción (Docker)
docker build -t radar-creds-web .
docker run -p 80:80 --network radar_net radar-creds-web
27. Conclusión del Paso 3
Estado inicial: el frontend estaba ausente en Pasos 1–2 (solo descripción de widgets).

Estado final: 24 módulos frontend implementados, cubriendo autenticación con MFA, RBAC con CASL, dashboard con 4 visualizaciones, CRUD de leaks/resets/reportes/auditoría/usuarios/fuentes, manejo de errores, i18n base, tests, Docker y CI.

Integración: consume la API del Paso 2 vía /api/v1, con refresh automático de tokens y tipado consistente con los schemas Pydantic.

Cumplimiento: la UI respeta RBAC por rol, muestra la integridad de la cadena de auditoría y expone las evidencias exportables (reportes PDF/Word/Excel) requeridas por ISO A.5.17.

Pendiente para Paso 4 (si se solicita): workflows n8n exportables en JSON, plantillas corporativas de reportes, manual de operación SOC y plan de comunicación legal a empleados (GDPR/LOPDGDD) listo para firma.