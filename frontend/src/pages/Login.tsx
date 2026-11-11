import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLogin, extractErrorMessage } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const schema = z.object({
  email: z.string().trim().min(1, "Correo electrónico requerido").email("Correo electrónico inválido"),
  password: z.string().min(1, "Contraseña requerida").min(8, "Mínimo 8 caracteres"),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const { register, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  const login = useLogin();

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-8">
      <Card className="w-full max-w-md overflow-hidden rounded-2xl border-slate-200 shadow-xl shadow-slate-200/60">
        <CardHeader className="border-b-0 bg-slate-950 px-7 py-8 text-white">
          <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-primary font-bold text-white">RC</div>
          <CardTitle className="text-xl text-white">Radar de Credenciales Comprometidas</CardTitle>
          <p className="mt-2 text-sm text-slate-300">Centro de operaciones para detectar y contener credenciales expuestas.</p>
        </CardHeader>
        <CardContent className="px-7 py-7">
          <form
            onSubmit={handleSubmit((d) => login.mutate(d))}
            className="space-y-4"
            aria-label="Formulario de acceso"
          >
            <div>
              <label htmlFor="email" className="text-sm font-medium">Correo corporativo</label>
              <Input
                id="email"
                type="text"
                inputMode="email"
                autoComplete="username"
                aria-invalid={Boolean(formState.errors.email)}
                aria-describedby="email-error"
                {...register("email")}
              />
              {formState.errors.email && (
                <p id="email-error" role="alert" className="text-destructive text-xs mt-1">
                  {formState.errors.email.message}
                </p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="text-sm font-medium">Contraseña</label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                aria-invalid={Boolean(formState.errors.password)}
                aria-describedby="password-error"
                {...register("password")}
              />
              {formState.errors.password && (
                <p id="password-error" role="alert" className="text-destructive text-xs mt-1">
                  {formState.errors.password.message}
                </p>
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
