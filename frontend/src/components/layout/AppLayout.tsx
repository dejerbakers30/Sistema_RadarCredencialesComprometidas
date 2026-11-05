import { useState } from "react";
import { Menu } from "lucide-react";
import { Outlet } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="flex min-h-screen flex-col md:pl-64">
        <Header />
        <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-2 md:hidden">
          <Button variant="outline" size="icon" aria-label="Abrir menú" onClick={() => setMobileOpen(true)}><Menu className="h-4 w-4" /></Button>
          <span className="text-sm font-semibold text-slate-800">Radar de Credenciales Comprometidas</span>
        </div>
        <main className="flex-1 overflow-auto px-4 py-5 sm:px-6 lg:px-8 lg:py-7"><Outlet /></main>
      </div>
    </div>
  );
}
