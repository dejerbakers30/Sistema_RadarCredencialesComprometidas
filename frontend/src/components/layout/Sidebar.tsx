import { NavLink } from "react-router-dom";
import { LayoutDashboard, ShieldAlert, RefreshCcw, FileBarChart2, ScrollText, Users, Database, Bell, UserCircle, X, ShieldCheck } from "lucide-react";
import { useCan } from "@/hooks/useCan";
import { cn } from "@/lib/utils";

interface Item { to: string; label: string; icon: React.ElementType; can?: () => boolean }

export function Sidebar({ mobileOpen = false, onClose }: { mobileOpen?: boolean; onClose?: () => void }) {
  const canReadLeaks = useCan("read", "leaks");
  const canReadResets = useCan("read", "resets");
  const canReadReports = useCan("read", "reports");
  const canReadAudit = useCan("read", "audit");
  const canReadUsers = useCan("read", "users");
  const canReadRoles = useCan("read", "roles");
  const canReadSources = useCan("read", "sources");
  const groups: { label: string; items: Item[] }[] = [
    { label: "Operación", items: [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }, { to: "/leaks", label: "Filtraciones", icon: ShieldAlert, can: () => canReadLeaks }, { to: "/resets", label: "Contenciones", icon: RefreshCcw, can: () => canReadResets }] },
    { label: "Análisis", items: [{ to: "/reports", label: "Reportes", icon: FileBarChart2, can: () => canReadReports }, { to: "/audit", label: "Auditoría", icon: ScrollText, can: () => canReadAudit }] },
    { label: "Administración", items: [{ to: "/users", label: "Usuarios", icon: Users, can: () => canReadUsers }, { to: "/roles", label: "Roles", icon: ShieldCheck, can: () => canReadRoles }, { to: "/sources", label: "Fuentes", icon: Database, can: () => canReadSources }] },
    { label: "Cuenta", items: [{ to: "/notifications", label: "Notificaciones", icon: Bell }, { to: "/profile", label: "Perfil", icon: UserCircle }] },
  ];
  return <>
    {mobileOpen && <button aria-label="Cerrar menú" className="fixed inset-0 z-30 bg-slate-950/30 md:hidden" onClick={onClose} />}
    <aside className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-200 bg-white shadow-xl transition-transform md:translate-x-0 md:shadow-none ${mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}>
      <div className="flex h-20 items-center justify-between border-b border-slate-100 px-5">
        <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-sm font-bold text-white">RC</div><div><span className="block text-sm font-bold leading-tight text-slate-900">Radar de</span><span className="block text-sm font-bold leading-tight text-primary">Credenciales</span></div></div>
        <button className="rounded-md p-1 text-slate-400 hover:bg-slate-100 md:hidden" onClick={onClose} aria-label="Cerrar menú"><X className="h-5 w-5" /></button>
      </div>
      <nav className="flex-1 space-y-6 overflow-y-auto p-4">
        {groups.map((group) => <div key={group.label}><p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">{group.label}</p><div className="space-y-1">{group.items.filter((i) => !i.can || i.can()).map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={onClose} className={({ isActive }) => cn("group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", isActive ? "bg-blue-50 text-primary" : "text-slate-600 hover:bg-slate-50 hover:text-slate-950")}><Icon className="h-4 w-4" />{label}</NavLink>)}</div></div>)}
      </nav>
      <div className="border-t border-slate-100 p-4 text-xs text-slate-400">Centro de operaciones<br /><span className="text-emerald-600">● Sistema operativo</span></div>
    </aside>
  </>;
}
