import { useMemo, useState } from "react";
import { UserPlus } from "lucide-react";
import { useUsers, useCreateUser, useUpdateUser } from "@/hooks/useUsers";
import { DataTable } from "@/components/common/DataTable";
import { FilterBar } from "@/components/common/FilterBar";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";
import { StatusIndicator } from "@/components/common/StatusIndicator";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useCan } from "@/hooks/useCan";

export default function Users() {
  const { data, isLoading, isError } = useUsers();
  const create = useCreateUser(); const update = useUpdateUser(); const canWrite = useCan("write", "users");
  const [open, setOpen] = useState(false); const [search, setSearch] = useState(""); const [role, setRole] = useState("");
  const [form, setForm] = useState({ email: "", nombre: "", rol: "end_user", password: "" });
  const rows = useMemo(() => (data ?? []).filter((user) => (!role || user.rol === role) && (!search || `${user.email} ${user.nombre}`.toLowerCase().includes(search.toLowerCase()))), [data, role, search]);
  const reset = () => { setForm({ email: "", nombre: "", rol: "end_user", password: "" }); setOpen(false); };
  return <div className="space-y-7"><PageHeader eyebrow="Administración" title="Usuarios" description="Gestiona el acceso corporativo y supervisa el estado de MFA." actions={canWrite && <Dialog open={open} onOpenChange={setOpen}><DialogTrigger asChild><Button><UserPlus className="h-4 w-4" />Nuevo usuario</Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>Crear usuario</DialogTitle></DialogHeader><div className="space-y-4"><Input aria-label="Email" placeholder="Email corporativo" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /><Input aria-label="Nombre" placeholder="Nombre completo" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /><Select aria-label="Rol" value={form.rol} onValueChange={(v) => setForm({ ...form, rol: v })}><option value="admin">Administrador</option><option value="soc_analyst">Analista SOC</option><option value="auditor">Auditor</option><option value="end_user">Usuario final</option></Select><Input aria-label="Contraseña" type="password" placeholder="Contraseña (opcional si SSO)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /><Button className="w-full" onClick={() => create.mutate(form, { onSuccess: reset })} disabled={!form.email || !form.nombre || create.isPending}>{create.isPending ? "Creando…" : "Crear usuario"}</Button></div></DialogContent></Dialog>} /><FilterBar search={search} onSearch={setSearch} onClear={() => { setSearch(""); setRole(""); }}><Select aria-label="Filtrar por rol" value={role} onValueChange={setRole}><option value="">Todos los roles</option><option value="admin">Administrador</option><option value="soc_analyst">Analista SOC</option><option value="auditor">Auditor</option><option value="end_user">Usuario final</option></Select></FilterBar><SectionCard title="Directorio corporativo" description={`${rows.length} usuarios visibles`}>{isError ? <div role="alert" className="text-sm text-rose-700">No se pudieron cargar los usuarios.</div> : <DataTable loading={isLoading} rows={rows} emptyText="No hay usuarios que coincidan con los filtros." columns={[{ key: "email", header: "Email", render: (r) => <span className="font-medium text-slate-800">{r.email}</span> }, { key: "nombre", header: "Nombre" }, { key: "rol", header: "Rol", render: (r) => <span className="capitalize">{r.rol?.replace("_", " ")}</span> }, { key: "activo", header: "Estado", render: (r) => <StatusIndicator value={r.activo ? "exitoso" : "fallido"} /> }, { key: "mfa_enabled", header: "MFA", render: (r) => r.mfa_enabled ? <span className="text-emerald-700">Activado</span> : <span className="text-slate-500">No configurado</span> }, { key: "acciones", header: "Acciones", render: (r) => canWrite && <Button variant="outline" size="sm" onClick={() => update.mutate({ id: r.id, data: { activo: !r.activo } })}>{r.activo ? "Desactivar" : "Activar"}</Button> }]} />}</SectionCard></div>;
}
