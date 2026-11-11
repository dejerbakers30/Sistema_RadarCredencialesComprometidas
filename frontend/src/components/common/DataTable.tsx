import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface Props<T> {
  rows: T[];
  columns: Column<T>[];
  loading?: boolean;
  error?: string;
  emptyText?: string;
  pagination?: {
    page: number;
    setPage: (n: number) => void;
    pageSize: number;
    hasMore: boolean;
  };
}

export function DataTable<T extends { id?: string | number }>({
  rows, columns, loading, error, emptyText = "Sin resultados", pagination,
}: Props<T>) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
      </div>
    );
  }
  if (error) {
    return <div role="alert" className="text-destructive text-sm">{error}</div>;
  }
  if (!rows.length) {
    return <div className="text-muted-foreground text-sm py-8 text-center">{emptyText}</div>;
  }

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto border rounded-md">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className={cn("text-left font-medium px-3 py-2", c.className)}>
                  {c.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={row.id ?? i} className="border-t hover:bg-muted/30">
                {columns.map((c) => (
                  <td key={c.key} className={cn("px-3 py-2", c.className)}>
                    {c.render ? c.render(row) : (row as any)[c.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={pagination.page === 0}
            onClick={() => pagination.setPage(pagination.page - 1)}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!pagination.hasMore}
            onClick={() => pagination.setPage(pagination.page + 1)}
          >
            Siguiente
          </Button>
        </div>
      )}
    </div>
  );
}
