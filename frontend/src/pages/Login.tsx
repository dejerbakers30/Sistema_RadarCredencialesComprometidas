import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLogin, extractErrorMessage } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const { register, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  const login = useLogin();

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Radar de Credenciales</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit((d) => login.mutate(d))}
            className="space-y-4"
            aria-label="Formulario de acceso"
          >
            <div>
              <label htmlFor="email" className="text-sm font-medium">Correo corporativo</label>
              <Input id="email" type="email" autoComplete="username" {...register("email")} />
              {formState.errors.email && (
                <p className="text-destructive text-xs mt-1">{formState.errors.email.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="text-sm font-medium">Contraseña</label>
              <Input id="password" type="password" autoComplete="current-password" {...register("password")} />
              {formState.errors.password && (
                <p className="text-destructive text-xs mt-1">{formState.errors.password.message}</p>
              )}
            </div>
            {login.isError && (
              <p role="alert" className="text-destructive text-sm">
                {extractErrorMessage(login.error)}
              </p>
            )}
            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? "Accediendo…" : "Acceder"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
