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
