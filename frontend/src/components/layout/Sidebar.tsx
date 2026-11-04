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
