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
