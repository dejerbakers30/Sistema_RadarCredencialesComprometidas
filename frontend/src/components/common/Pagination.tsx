import { Button } from "@/components/ui/button";

interface Props {
  page: number;
  setPage: (n: number) => void;
  hasMore: boolean;
  pageSize?: number;
  total?: number;
}

export function Pagination({ page, setPage, hasMore, pageSize = 25, total }: Props) {
  return (
    <div className="flex items-center justify-between gap-2 py-2">
      <div className="text-sm text-muted-foreground">
        Página {page + 1} · {pageSize} por página
        {typeof total === "number" && ` · ${total} registros`}
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
        >
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!hasMore}
          onClick={() => setPage(page + 1)}
        >
          Siguiente
        </Button>
      </div>
    </div>
  );
}
