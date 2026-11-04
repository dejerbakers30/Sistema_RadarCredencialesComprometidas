import { useState } from "react";
import { useResets, useManualReset } from "@/hooks/useResets";
import { DataTable } from "@/components/common/DataTable";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useCan } from "@/hooks/useCan";
import { formatDateTime } from "@/lib/format";

export default function ResetsList() {
  const { data, isLoading } = useResets();
  const manual = useManualReset();
  const canExecute = useCan("execute", "resets");
  const [open, setOpen] = useState(false);
  const [leakId, setLeakId] = useState("");
  const [motivo, setMotivo] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Contenciones ejecutadas</h1>
        {canExecute && (
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>Contención manual</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle>Forzar contención</DialogTitle></DialogHeader>
              <div className="space-y-3">
                <Input placeholder="ID de leak_hit" value={leakId} onChange={(e) => setLeakId(e.target.value)} />
                <Input placeholder="Motivo (opcional)" value={motivo} onChange={(e) => setMotivo(e.target.value)} />
                <Button
                  onClick={() => manual.mutate({ leak_hit_id: leakId, motivo }, {
                    onSuccess: () => { setOpen(false); setLeakId(""); setMotivo(""); },
                  })}
                  disabled={!leakId || manual.isPending}
                >
                  Ejecutar
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
          { key: "leak_hit_id", header: "Leak" },
          { key: "metodo", header: "Método" },
          { key: "resultado", header: "Resultado" },
          { key: "intentos", header: "Intentos" },
          { key: "timestamp", header: "Fecha", render: (r) => formatDateTime(r.timestamp) },
          { key: "proximo_intento", header: "Próximo intento", render: (r) => r.proximo_intento ? formatDateTime(r.proximo_intento) : "—" },
        ]}
      />
    </div>
  );
}
