import { useNavigate } from "react-router-dom";
import { FolderPlus } from "lucide-react";
import { Etiqueta } from "../Common/Etiqueta";
import { EstadoVacio } from "../Common/EstadoVacio";
import { formatDate } from "../../utils/formatters";
import { truncate } from "../../utils/helpers";
import { ROUTES } from "../../constants/rutas";

export function RejillaIncidencias({ items = [], loading }) {
  const navigate = useNavigate();
  if (!loading && !items.length) {
    return (
      <EstadoVacio
        icon={FolderPlus}
        titulo="Sin incidencias"
        descripcion="No hay incidencias con los filtros seleccionados."
      />
    );
  }
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <div
          key={item.id}
          onClick={() => navigate(ROUTES.incidenciaDetail(item.id))}
          className="card card-hover flex cursor-pointer flex-col gap-3 p-5 animate-fade-in"
        >
          <div className="flex items-start justify-between gap-2">
            <span className="text-xs font-semibold text-iq-sub">INC-{item.id}</span>
            <div className="flex gap-1.5">
              <Etiqueta type="prioridad" value={item.prioridad} />
              <Etiqueta type="estado" value={item.estado} dot />
            </div>
          </div>
          <h4 className="line-clamp-2 text-sm font-semibold text-iq-text">
            {item.titulo}
          </h4>
          <div className="mt-auto flex items-center justify-between pt-2">
            <Etiqueta type="categoria" value={item.categoria} />
            <span className="text-xs text-iq-sub">{formatDate(item.creado_en)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}