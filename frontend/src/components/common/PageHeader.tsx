import { Breadcrumbs } from "@/components/layout/Breadcrumbs";

interface Props {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ eyebrow, title, description, actions }: Props) {
  return (
    <div className="space-y-4">
      <Breadcrumbs />
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          {eyebrow && <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">{eyebrow}</p>}
          <h1 className="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">{title}</h1>
          {description && <p className="max-w-2xl text-sm text-slate-500">{description}</p>}
        </div>
        {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}

export function SectionCard({ title, description, action, children, className = "" }: {
  title: string;
  description?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      <div className="flex flex-col gap-2 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
          {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
        </div>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

export function EmptyState({ title = "Sin resultados", description, icon: Icon, action }: {
  title?: string;
  description?: string;
  icon?: React.ElementType;
  action?: React.ReactNode;
}) {
  const EmptyIcon = Icon;
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-slate-200 bg-slate-50/60 px-6 py-10 text-center">
      {EmptyIcon && <EmptyIcon className="h-8 w-8 text-slate-400" aria-hidden="true" />}
      <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      {description && <p className="max-w-sm text-xs text-slate-500">{description}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ message = "No pudimos cargar la información.", onRetry }: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
      <div className="flex items-center justify-between gap-4">
        <span>{message}</span>
        {onRetry && <button className="font-semibold underline" onClick={onRetry}>Reintentar</button>}
      </div>
    </div>
  );
}

export function LoadingState({ label = "Cargando información…" }: { label?: string }) {
  return <div role="status" className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-500"><span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-primary" />{label}</div>;
}
