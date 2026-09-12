import { useNavigate } from "react-router-dom";
import { ArrowUpDown } from "lucide-react";
import { Etiqueta } from "../Common/Etiqueta";
import { EstadoVacio } from "../Common/EstadoVacio";
import { Inbox } from "lucide-react";
import { formatDate } from "../../utils/formatters";
import { ROUTES } from "../../constants/rutas";

export function TablaIncidencias({ items = [], sortBy, order, onSort, loading }) {
  const navigate = useNavigate();
  const cols = [
    { key: "id", label: "ID" },
    { key: "titulo", label: "Título" },
    { key: "estado", label: "Estado" },
    { key: "prioridad", label: "Prioridad" },
    { key: "categoria", label: "Categoría" },
    { key: "creado_en", label: "Creada" },
    { key: "actualizado_en", label: "Actualizada" },
  ];

  if (!loading && !items.length) {
    return <EstadoVacio icon={Inbox} titulo="Sin incidencias" descripcion="No hay incidencias con los filtros seleccionados." />;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-iq-border bg-gray-50/50">
            {cols.map((col) => (
              <th
                key={col.key}
                className="table-th cursor-pointer select-none hover:text-iq-text"
                onClick={() =>
                  onSort(
                    col.key,
                    sortBy === col.key && order === "asc" ? "desc" : "asc"
                  )
                }
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  <ArrowUpDown
                    size={12}
                    className={sortBy === col.key ? "text-iq-primary" : "text-gray-300"}
                  />
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              onClick={() => navigate(ROUTES.incidenciaDetail(item.id))}
              className="cursor-pointer border-b border-iq-border transition-colors duration-150 last:border-0 hover:bg-iq-hover"
            >
              <td className="table-td font-medium text-iq-text">INC-{item.id}</td>
              <td className="table-td max-w-[320px] truncate font-medium text-iq-text">
                {item.titulo}
              </td>
              <td className="table-td">
                <Etiqueta type="estado" value={item.estado} dot />
              </td>
              <td className="table-td">
                <Etiqueta type="prioridad" value={item.prioridad} />
              </td>
              <td className="table-td">
                <Etiqueta type="categoria" value={item.categoria} />
              </td>
              <td className="table-td text-iq-sub">{formatDate(item.creado_en)}</td>
              <td className="table-td text-iq-sub">{timeAgoShort(item.actualizado_en)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function timeAgoShort(iso) {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "ahora";
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}