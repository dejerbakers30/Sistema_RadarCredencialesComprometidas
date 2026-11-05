import { useState } from "react";
import { Eye, EyeOff, ShieldCheck } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { extractErrorMessage } from "@/lib/api";
import { PageHeader, SectionCard } from "@/components/common/PageHeader";

interface EnrollResponse {
  secret: string;
  otpauth_url: string;
}

export default function Profile() {
  const user = useAuthStore((s) => s.user);
  const toast = useToast();
  const [code, setCode] = useState("");
  const [showSecret, setShowSecret] = useState(false);

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
    <div className="space-y-7">
      <PageHeader eyebrow="Cuenta" title="Mi perfil" description="Consulta tu identidad y administra las opciones de seguridad disponibles para tu cuenta." />
      <SectionCard title="Datos de cuenta" description="Información visible de tu sesión actual.">
        <div className="grid gap-5 text-sm sm:grid-cols-2">
          <div><div className="text-xs font-medium uppercase tracking-wide text-slate-400">Nombre</div><div className="mt-1 font-medium text-slate-800">{user?.nombre ?? "—"}</div></div>
          <div><div className="text-xs font-medium uppercase tracking-wide text-slate-400">Email</div><div className="mt-1 font-medium text-slate-800">{user?.email ?? "—"}</div></div>
          <div><div className="text-xs font-medium uppercase tracking-wide text-slate-400">Rol</div><div className="mt-1 font-medium text-slate-800">{user?.rol ?? "—"}</div></div>
          <div><div className="text-xs font-medium uppercase tracking-wide text-slate-400">MFA</div><div className="mt-1 font-medium text-slate-800">{user?.mfa_enabled ? "Activado" : "Desactivado"}</div></div>
        </div>
      </SectionCard>

      {!user?.mfa_enabled && (
        <SectionCard title="Activar MFA (TOTP)" description="Añade una segunda capa de verificación con una aplicación autenticadora.">
          <div className="space-y-3">
            {!enroll.data ? (
              <Button onClick={() => enroll.mutate()} disabled={enroll.isPending}>
                {enroll.isPending ? "Generando…" : "Generar secreto"}
              </Button>
            ) : (
              <>
                <p className="text-sm text-muted-foreground">
                  Añade este secreto a tu app autenticadora y luego introduce el código.
                </p>
                <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2">
                  <code className="min-w-0 flex-1 break-all text-xs text-slate-700">{showSecret ? enroll.data.secret : "••••••••••••••••"}</code>
                  <Button type="button" variant="ghost" size="sm" onClick={() => setShowSecret((value) => !value)} aria-label={showSecret ? "Ocultar secreto MFA" : "Mostrar secreto MFA"}>
                    {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                <Input
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="Código de 6 dígitos"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
                <Button onClick={() => verify.mutate(code)} disabled={code.length !== 6 || verify.isPending}>
                  <ShieldCheck className="h-4 w-4" />
                  Verificar y activar
                </Button>
              </>
            )}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
