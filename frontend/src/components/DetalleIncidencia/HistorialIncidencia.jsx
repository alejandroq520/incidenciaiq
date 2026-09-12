import { History } from "lucide-react";
import { formatDate } from "../../utils/formatters";

export function HistorialIncidencia({ items = [] }) {
  return (
    <div className="card p-5">
      <h3 className="mb-4 flex items-center gap-2 text-base font-semibold text-iq-text">
        <History size={16} className="text-iq-sub" />
        Historial de cambios
      </h3>
      {items.length ? (
        <ol className="relative space-y-4 border-l border-iq-border pl-5">
          {items.map((h, idx) => (
            <li key={idx} className="relative">
              <span
                className="absolute -left-[26px] top-1 flex h-3 w-3 items-center justify-center rounded-full border-2 border-white bg-iq-primary"
                style={{ boxShadow: "0 0 0 1px #E5E7EB" }}
              />
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium text-iq-text">{h.accion}</span>
                {h.valor_nuevo && (
                  <span className="rounded-full bg-iq-hover px-2 py-0.5 text-xs font-medium text-iq-body">
                    {h.valor_nuevo}
                  </span>
                )}
              </div>
              <p className="text-xs text-iq-sub">
                {formatDate(h.fecha)} · {h.cambiado_por}
              </p>
            </li>
          ))}
        </ol>
      ) : (
        <p className="text-sm text-iq-sub">Sin cambios registrados.</p>
      )}
    </div>
  );
}