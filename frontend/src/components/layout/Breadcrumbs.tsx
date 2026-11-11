import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const LABELS: Record<string, string> = {
  dashboard: "Panel",
  leaks: "Filtraciones",
  resets: "Contenciones",
  reports: "Reportes",
  audit: "Auditoría",
  users: "Usuarios",
  roles: "Roles",
  sources: "Fuentes",
  profile: "Perfil",
  notifications: "Notificaciones",
};

export function Breadcrumbs() {
  const { pathname } = useLocation();
  const segments = pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm">
      <Link to="/dashboard" className="text-muted-foreground hover:text-foreground">
        Inicio
      </Link>
      {segments.map((seg, i) => {
        const to = "/" + segments.slice(0, i + 1).join("/");
        const label = LABELS[seg] ?? seg;
        const isLast = i === segments.length - 1;
        return (
          <span key={to} className="flex items-center gap-1">
            <ChevronRight className="h-3 w-3 text-muted-foreground" />
            {isLast ? (
              <span className="font-medium">{label}</span>
            ) : (
              <Link to={to} className="text-muted-foreground hover:text-foreground">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
