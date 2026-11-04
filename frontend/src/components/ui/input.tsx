// input.tsx
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-md border bg-background px-3 py-2 text-sm",
        "focus:outline-none focus:ring-2 focus:ring-primary/40",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
