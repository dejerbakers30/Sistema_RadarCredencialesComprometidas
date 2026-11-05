import { useForm } from "react-hook-form";
import { useAuthStore } from "@/stores/authStore";
import { useMfaVerify } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Navigate } from "react-router-dom";

export default function MfaVerify() {
  const pending = useAuthStore((s) => s.mfaPendingEmail);
  const [email, challengeToken] = (pending ?? "|").split("|", 2);
  const { register, handleSubmit } = useForm<{ code: string }>();
  const mfa = useMfaVerify();

  if (!email) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader><CardTitle>Verificación en dos pasos</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit((d) => mfa.mutate({ email, code: d.code, challenge_token: challengeToken }))} className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Introduce el código de 6 dígitos de tu aplicación autenticadora.
            </p>
            <Input
              inputMode="numeric"
              maxLength={6}
              pattern="\d{6}"
              autoFocus
              {...register("code")}
            />
            <Button type="submit" className="w-full" disabled={mfa.isPending}>Verificar</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
