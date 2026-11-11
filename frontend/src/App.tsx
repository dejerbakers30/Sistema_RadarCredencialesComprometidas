import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { AbilityContext } from "@/hooks/useCan";
import { buildAbility } from "@/lib/abilities";
import { useAuthStore } from "@/stores/authStore";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import Login from "@/pages/Login";
import MfaVerify from "@/pages/MfaVerify";
const Dashboard = lazy(() => import("@/pages/Dashboard"));
const LeaksList = lazy(() => import("@/pages/LeaksList"));
const LeakDetail = lazy(() => import("@/pages/LeakDetail"));
const ResetsList = lazy(() => import("@/pages/ResetsList"));
const Reports = lazy(() => import("@/pages/Reports"));
const AuditLog = lazy(() => import("@/pages/AuditLog"));
const Users = lazy(() => import("@/pages/Users"));
const Roles = lazy(() => import("@/pages/Roles"));
const Sources = lazy(() => import("@/pages/Sources"));
const Profile = lazy(() => import("@/pages/Profile"));
const Notifications = lazy(() => import("@/pages/Notifications"));
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
              <Route element={<LazyPageBoundary />}>
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
              </Route>
              <Route element={<ProtectedRoute action="read" subject="roles" />}>
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
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AbilityContext.Provider>
  );
}

function LazyPageBoundary() {
  return <Suspense fallback={<div className="p-8"><div className="h-6 w-48 animate-pulse rounded bg-slate-200" /></div>}><Outlet /></Suspense>;
}
