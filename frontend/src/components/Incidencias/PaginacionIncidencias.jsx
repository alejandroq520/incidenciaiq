import { ChevronLeft, ChevronRight } from "lucide-react";
import { cx } from "../../utils/helpers";

export function PaginacionIncidencias({ total, page, pageSize, onChange }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const windowStart = Math.max(1, page - 2);
  const windowEnd = Math.min(pages, page + 2);
  const list = [];
  for (let i = windowStart; i <= windowEnd; i++) list.push(i);

  if (pages <= 1) return null;

  return (
    <div className="flex items-center justify-between gap-4 px-1 pt-1">
      <p className="text-xs text-iq-sub">
        Mostrando {total === 0 ? 0 : (page - 1) * pageSize + 1}–
        {Math.min(page * pageSize, total)} de {total} resultados
      </p>
      <div className="flex items-center gap-1">
        <button
          className="btn-secondary !px-2.5 !py-1.5"
          disabled={page === 1}
          onClick={() => onChange(page - 1)}
          aria-label="Anterior"
        >
          <ChevronLeft size={16} />
        </button>
        {list.map((p) => (
          <button
            key={p}
            onClick={() => onChange(p)}
            className={cx(
              "h-8 w-8 rounded-lg text-sm font-medium transition-colors",
              p === page
                ? "bg-iq-primary text-white"
                : "text-iq-body hover:bg-iq-hover"
            )}
          >
            {p}
          </button>
        ))}
        <button
          className="btn-secondary !px-2.5 !py-1.5"
          disabled={page === pages}
          onClick={() => onChange(page + 1)}
          aria-label="Siguiente"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}