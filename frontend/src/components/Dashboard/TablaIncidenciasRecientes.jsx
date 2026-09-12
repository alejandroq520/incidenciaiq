import { useNavigate } from "react-router-dom";
import { Etiqueta } from "../Common/Etiqueta";
import { timeAgo } from "../../utils/formatters";
import { ROUTES } from "../../constants/rutas";

export function TablaIncidenciasRecientes({ items = [] }) {
  const navigate = useNavigate();
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-iq-border bg-gray-50/50">
            <th className="table-th">ID</th>
            <th className="table-th">Título</th>
            <th className="table-th">Estado</th>
            <th className="table-th">Prioridad</th>
            <th className="table-th">Categoría</th>
            <th className="table-th">Creada</th>
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
              <td className="table-td max-w-[280px] truncate font-medium text-iq-text">
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
              <td className="table-td text-iq-sub">{timeAgo(item.creado_en)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}