// Forbidden.tsx
import { Link } from "react-router-dom";

export default function Forbidden() {
  return (
    <div className="text-center py-20 space-y-3">
      <h1 className="text-3xl font-semibold">403</h1>
      <p className="text-muted-foreground">No tienes permisos para acceder a esta sección.</p>
      <Link to="/dashboard" className="text-primary hover:underline">Volver al panel</Link>
    </div>
  );
}
