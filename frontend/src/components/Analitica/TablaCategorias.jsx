import { EstadoVacio } from "../Common/EstadoVacio";
import { Inbox } from "lucide-react";
import { formatResolution } from "../../utils/formatters";

export function TablaCategorias({ data = [], resolutionPorCategoria = [] }) {
  const resMap = Object.fromEntries(
    (resolutionPorCategoria || []).map((r) => [r.categoria, r.average_hours])
  );

  if (!data.length) {
    return <EstadoVacio icon={Inbox} titulo="Sin datos" descripcion="No hay incidencias en el periodo seleccionado." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-iq-border bg-gray-50/50">
            <th className="table-th">Categoría</th>
            <th className="table-th">Total</th>
            <th className="table-th">Abiertas</th>
            <th className="table-th">Cerradas</th>
            <th className="table-th">% Resueltas</th>
            <th className="table-th">Tiempo promedio</th>
          </tr>
        </thead>
        <tbody>
          {data.map((c, i) => {
            const pct = c.total ? Math.round((c.closed / c.total) * 100) : 0;
            const avgH = resMap[c.name];
            return (
              <tr
                key={c.name}
                className={`border-b border-iq-border last:border-0 ${i % 2 === 1 ? "bg-gray-50/40" : ""}`}
              >
                <td className="table-td">
                  <span className="inline-flex items-center gap-2 font-medium text-iq-text">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ background: c.color }} />
                    {c.name}
                  </span>
                </td>
                <td className="table-td font-semibold text-iq-text">{c.total}</td>
                <td className="table-td text-red-600">{c.opened}</td>
                <td className="table-td text-green-600">{c.closed}</td>
                <td className="table-td">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-iq-hover">
                      <div
                        className="h-full rounded-full bg-iq-success"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-iq-sub">{pct}%</span>
                  </div>
                </td>
                <td className="table-td">
                  {avgH != null ? `${avgH}h` : formatResolution(null)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}