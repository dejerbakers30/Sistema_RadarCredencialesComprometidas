import { useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api";

interface EnrollResponse {
  secret: string;
  otpauth_url: string;
}

export default function Profile() {
  const user = useAuthStore((s) => s.user);
  const toast = useToast();
  const [code, setCode] = useState("");

  const enroll = useMutation({
    mutationFn: async () => (await api.post<EnrollResponse>("/auth/mfa/enroll")).data,
  });

  const verify = useMutation({
    mutationFn: async (c: string) =>
      (await api.post("/auth/mfa/verify-enroll", { code: c })).data,
    onSuccess: () => toast.push({ title: "MFA activado", tone: "success" }),
    onError: (e) => toast.push({ title: "Error", description: extractErrorMessage(e), tone: "danger" }),
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <Card>
        <CardHeader><CardTitle>Datos de cuenta</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <div><div className="text-muted-foreground text-xs">Nombre</div>{user?.nombre}</div>
          <div><div className="text-muted-foreground text-xs">Email</div>{user?.email}</div>
          <div><div className="text-muted-foreground text-xs">Rol</div>{user?.rol}</div>
          <div><div className="text-muted-foreground text-xs">MFA</div>{user?.mfa_enabled ? "Activado" : "Desactivado"}</div>
        </CardContent>
      </Card>

      {!user?.mfa_enabled && (
        <Card>
          <CardHeader><CardTitle>Activar MFA (TOTP)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {!enroll.data ? (
              <Button onClick={() => enroll.mutate()} disabled={enroll.isPending}>
                {enroll.isPending ? "Generando…" : "Generar secreto"}
              </Button>
            ) : (
              <>
                <p className="text-sm text-muted-foreground">
                  Añade este secreto a tu app autenticadora y luego introduce el código.
                </p>
                <code className="block p-2 bg-muted rounded text-xs break-all">{enroll.data.secret}</code>
                <Input
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="Código de 6 dígitos"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
                <Button onClick={() => verify.mutate(code)} disabled={code.length !== 6 || verify.isPending}>
                  Verificar y activar
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
