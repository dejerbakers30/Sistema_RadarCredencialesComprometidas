import { Inbox } from "lucide-react";

interface Props {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  title = "Sin resultados",
  description,
  action,
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      <Inbox className="h-10 w-10 text-muted-foreground" />
      <h3 className="text-sm font-medium">{title}</h3>
      {description && <p className="text-xs text-muted-foreground max-w-sm">{description}</p>}
      {action}
    </div>
  );
}
