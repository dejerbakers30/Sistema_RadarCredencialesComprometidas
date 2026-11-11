import { createContext, useCallback, useContext, useState } from "react";
import * as ToastPrimitive from "@radix-ui/react-toast";
import { cn } from "@/lib/utils";

type Tone = "default" | "success" | "danger";
interface Toast { id: number; title: string; description?: string; tone?: Tone }

interface ToastContextValue { push: (t: Omit<Toast, "id">) => void }
const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const push = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now();
    setItems((prev) => [...prev, { ...t, id }]);
    setTimeout(() => setItems((prev) => prev.filter((i) => i.id !== id)), 5000);
  }, []);

  return (
    <ToastContext.Provider value={{ push }}>
      <ToastPrimitive.Provider swipeDirection="right">
        {children}
        {items.map((t) => (
          <ToastPrimitive.Root
            key={t.id}
            open
            onOpenChange={() => setItems((prev) => prev.filter((i) => i.id !== t.id))}
            className={cn(
              "fixed bottom-4 right-4 rounded-md border p-4 shadow-lg bg-background",
              t.tone === "success" && "border-emerald-400",
              t.tone === "danger" && "border-rose-400"
            )}
          >
            <ToastPrimitive.Title className="font-medium">{t.title}</ToastPrimitive.Title>
            {t.description && (
              <ToastPrimitive.Description className="text-sm text-muted-foreground">
                {t.description}
              </ToastPrimitive.Description>
            )}
          </ToastPrimitive.Root>
        ))}
        <ToastPrimitive.Viewport className="fixed bottom-4 right-4 z-50" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast debe usarse dentro de ToastProvider");
  return ctx;
}
