import { Bell, LogOut, UserCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useLogout } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Breadcrumbs } from "./Breadcrumbs";

export function Header() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6">
      <Breadcrumbs />
      <div className="flex items-center gap-2 sm:gap-4">
        <Link to="/notifications" className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100" aria-label="Notificaciones"><Bell className="h-5 w-5" /><span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-primary" /></Link>
        <div className="hidden text-right sm:block"><div className="text-sm font-semibold text-slate-800">{user?.nombre}</div><div className="text-xs capitalize text-slate-500">{user?.rol?.replace("_", " ")}</div></div>
        <Link to="/profile" className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-50 text-primary" aria-label="Abrir perfil"><UserCircle className="h-5 w-5" /></Link>
        <Button variant="ghost" size="icon" onClick={logout} aria-label="Cerrar sesión"><LogOut className="h-4 w-4" /></Button>
      </div>
    </header>
  );
}
