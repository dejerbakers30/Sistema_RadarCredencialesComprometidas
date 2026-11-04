import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ROLES = [
  { nombre: "Admin", permisos: ["Todo el sistema", "Gestión de usuarios y roles", "Configuración"] },
  { nombre: "Analista SOC", permisos: ["Ver y editar leaks", "Ejecutar contenciones", "Generar reportes", "Ver auditoría"] },
  { nombre: "Auditor", permisos: ["Lectura total", "Exportar reportes y auditoría"] },
  { nombre: "Usuario final", permisos: ["Ver sus notificaciones", "Editar su perfil"] },
];

export default function Roles() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Roles y permisos</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {ROLES.map((r) => (
          <Card key={r.nombre}>
            <CardHeader><CardTitle>{r.nombre}</CardTitle></CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 text-sm space-y-1">
                {r.permisos.map((p) => <li key={p}>{p}</li>)}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
