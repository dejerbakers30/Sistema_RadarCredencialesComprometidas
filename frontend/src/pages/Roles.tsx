import { ShieldCheck, Users } from "lucide-react";
import { useRoles } from "@/hooks/useRoles";
import { EmptyState, ErrorState, LoadingState, PageHeader, SectionCard } from "@/components/common/PageHeader";

export default function Roles() {
  const { data: roles, isLoading, isError } = useRoles();
  return <div className="space-y-7"><PageHeader eyebrow="Administración" title="Roles y permisos" description="Consulta la autorización persistida en el backend para cada perfil operativo." />{isLoading && <LoadingState label="Cargando roles y permisos…" />}{isError && <ErrorState message="No se pudieron cargar los roles." />} {!isLoading && !isError && !roles?.length && <EmptyState icon={ShieldCheck} title="Sin roles disponibles" description="No hay roles devueltos por la API." />}<div className="grid gap-5 lg:grid-cols-2">{roles?.map((role) => <SectionCard key={role.nombre} title={role.nombre.replace("_", " ")} description={role.descripcion ?? "Perfil de autorización del sistema"} action={<span className="inline-flex items-center gap-1 text-xs text-slate-500"><Users className="h-3.5 w-3.5" />{role.usuarios.length} usuarios</span>}><div className="flex flex-wrap gap-2">{role.permisos.map((permission) => <span key={`${permission.modulo}:${permission.accion}`} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{permission.modulo} · {permission.accion}</span>)}</div></SectionCard>)}</div></div>;
}
