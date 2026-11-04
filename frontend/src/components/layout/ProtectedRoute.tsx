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
