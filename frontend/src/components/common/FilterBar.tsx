import { RotateCcw, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function FilterBar({ search, onSearch, onClear, children }: {
  search?: string;
  onSearch?: (value: string) => void;
  onClear: () => void;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:flex-row lg:items-center">
      {onSearch && <div className="relative min-w-0 flex-1 lg:max-w-sm"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" /><Input aria-label="Buscar" className="pl-9" placeholder="Buscar…" value={search ?? ""} onChange={(e) => onSearch(e.target.value)} /></div>}
      <div className="flex flex-wrap items-center gap-2">{children}</div>
      <Button type="button" variant="outline" size="sm" onClick={onClear} className="self-start lg:ml-auto"><RotateCcw className="h-4 w-4" />Limpiar filtros</Button>
    </div>
  );
}
