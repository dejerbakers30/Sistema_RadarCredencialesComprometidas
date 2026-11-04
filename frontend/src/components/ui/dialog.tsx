// dialog.tsx — wrapper Radix
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogContent = ({ className, ...props }: DialogPrimitive.DialogContentProps) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 bg-black/40 z-40" />
    <DialogPrimitive.Content
      className={cn("fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background rounded-lg p-6 w-full max-w-md z-50", className)}
      {...props}
    />
  </DialogPrimitive.Portal>
);
export const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("mb-4", className)} {...props} />
);
export const DialogTitle = DialogPrimitive.Title;
