import { useState } from "react";
import { useUsers, useCreateUser, useUpdateUser } from "@/hooks/useUsers";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useCan } from "@/hooks/useCan";

export default function Users() {
  const { data, isLoading } = useUsers();
  const create = useCreateUser();
  const update = useUpdateUser();
  const canWrite = useCan("write", "users");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ email: "", nombre: "", rol: "end_user", password: "" });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Usuarios</h1>
        {canWrite && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild><Button>Nuevo usuario</Button></DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Crear usuario</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                <Input placeholder="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
                <Select value={form.rol} onValueChange={(v) => setForm({ ...form, rol: v })}>
                  <option value="admin">Admin</option>
                  <option value="soc_analyst">Analista SOC</option>
                  <option value="auditor">Auditor</option>
                  <option value="end_user">Usuario final</option>
                </Select>
                <Input type="password" placeholder="Contraseña (opcional si SSO)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
                <Button
                  onClick={() => create.mutate(form, { onSuccess: () => { setOpen(false); setForm({ email: "", nombre: "", rol: "end_user", password: "" }); } })}
                  disabled={!form.email || !form.nombre || create.isPending}
                >
                  Crear
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <DataTable
        loading={isLoading}
        rows={data ?? []}
        columns={[
          { key: "email", header: "Email" },
          { key: "nombre", header: "Nombre" },
          { key: "activo", header: "Activo", render: (r) => r.activo ? <Badge>Activo</Badge> : <Badge variant="destructive">Inactivo</Badge> },
          { key: "mfa_enabled", header: "MFA", render: (r) => r.mfa_enabled ? "Sí" : "No" },
          {
            key: "acciones",
            header: "",
            render: (r) => canWrite && (
              <Button variant="outline" size="sm" onClick={() => update.mutate({ id: r.id, data: { activo: !r.activo } })}>
                {r.activo ? "Desactivar" : "Activar"}
              </Button>
            ),
          },
        ]}
      />
    </div>
  );
}
