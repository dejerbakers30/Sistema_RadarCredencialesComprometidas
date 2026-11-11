import { cn } from "@/lib/utils";

export function Badge({ children, className, variant = "default" }: {
  children: React.ReactNode; className?: string; variant?: "default" | "destructive";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        variant === "destructive" ? "bg-rose-100 text-rose-800" : "bg-muted text-foreground",
        className
      )}
    >
      {children}
    </span>
  );
}
