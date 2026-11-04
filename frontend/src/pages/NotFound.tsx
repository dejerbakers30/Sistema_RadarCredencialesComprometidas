// NotFound.tsx
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="text-center py-20 space-y-3">
      <h1 className="text-3xl font-semibold">404</h1>
      <p className="text-muted-foreground">La página no existe.</p>
      <Link to="/dashboard" className="text-primary hover:underline">Volver al panel</Link>
    </div>
  );
}
