// select.tsx (simplificado sobre <select> nativo)
import { cn } from "@/lib/utils";

interface Props extends React.SelectHTMLAttributes<HTMLSelectElement> {
  onValueChange?: (v: string) => void;
}

export function Select({ className, onValueChange, children, ...props }: Props) {
  return (
    <select
      className={cn("h-10 rounded-md border bg-background px-3 text-sm", className)}
      onChange={(e) => onValueChange?.(e.target.value)}
      {...props}
    >
      {children}
    </select>
  );
}
