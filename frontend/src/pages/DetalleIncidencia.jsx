import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { servicioIncidencias } from "../services/servicioIncidencias";
import { useNotificacion } from "../context/contextoNotificacion";
import { Etiqueta } from "../components/Common/Etiqueta";
import { Spinner } from "../components/Common/Spinner";
import { Boton } from "../components/Common/Boton";
import { TarjetaAnalisisIA } from "../components/DetalleIncidencia/TarjetaAnalisisIA";
import { HistorialIncidencia } from "../components/DetalleIncidencia/HistorialIncidencia";
import { formatDate, formatResolution } from "../utils/formatters";
import { ID_ESTADO_CERRADO } from "../constants/estados";

export default function DetalleIncidencia() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error } = useNotificacion();
  const [incidencia, setIncidencia] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingState, setSavingState] = useState(false);
  const [savingPriority, setSavingPriority] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    servicioIncidencias
      .get(id)
      .then((data) => {
        if (active) setIncidencia(data);
      })
      .catch((e) => {
        error(e.message || "No se pudo cargar la incidencia");
        navigate("/incidencias");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!incidencia) return null;

  const changeState = async (estadoId) => {
    setSavingState(true);
    try {
      const updated = await servicioIncidencias.update(id, {
        estado_id: Number(estadoId),
        creado_por: "Alejandro",
      });
      setIncidencia(updated);
      if (Number(estadoId) === ID_ESTADO_CERRADO) {
        success(`Incidencia INC-${id} cerrada en ${formatResolution(updated.tiempo_resolucion_minutos)}`);
      } else {
        success("Estado actualizado");
      }
    } catch (e) {
      error(e.message);
    } finally {
      setSavingState(false);
    }
  };

  const changePriority = async (prioridadId) => {
    setSavingPriority(true);
    try {
      const updated = await servicioIncidencias.update(id, {
        prioridad_id: Number(prioridadId),
        creado_por: "Alejandro",
      });
      setIncidencia(updated);
      success("Prioridad actualizada");
    } catch (e) {
      error(e.message);
    } finally {
      setSavingPriority(false);
    }
  };

  const confirmarAnalisis = async () => {
    try {
      const updated = await servicioIncidencias.confirmarAnalisis(id, true);
      setIncidencia(updated);
      success("Clasificación confirmada");
    } catch (e) {
      error(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate("/incidencias")}
          className="btn-secondary !px-3"
        >
          <ArrowLeft size={16} />
          Volver
        </button>
        <p className="text-sm text-iq-sub">
          Incidencias &gt; <span className="font-medium text-iq-text">INC-{incidencia.id}</span>
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="card p-6">
            <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
              <h2 className="text-2xl font-bold text-iq-text">{incidencia.titulo}</h2>
              <div className="flex gap-2">
                <Etiqueta type="estado" value={incidencia.estado.name} dot />
                <Etiqueta type="prioridad" value={incidencia.prioridad.name} />
              </div>
            </div>
            <div className="mb-5 flex flex-wrap gap-x-6 gap-y-1 text-sm text-iq-sub">
              <span>
                Creada: <span className="text-iq-body">{formatDate(incidencia.creado_en)}</span>
              </span>
              <span>
                Actualizada: <span className="text-iq-body">{formatDate(incidencia.actualizado_en)}</span>
              </span>
              <span>
                Por: <span className="text-iq-body">{incidencia.creado_por}</span>
              </span>
            </div>

            <div className="mb-6 space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-iq-sub">
                    Estado
                  </label>
                  <select
                    className="select"
                    value={incidencia.estado.id}
                    onChange={(e) => changeState(e.target.value)}
                    disabled={savingState}
                  >
                    <option value={1}>Abierta</option>
                    <option value={2}>Pendiente</option>
                    <option value={3}>Cerrada</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-iq-sub">
                    Prioridad
                  </label>
                  <select
                    className="select"
                    value={incidencia.prioridad.id}
                    onChange={(e) => changePriority(e.target.value)}
                    disabled={savingPriority}
                  >
                    <option value={1}>Baja</option>
                    <option value={2}>Media</option>
                    <option value={3}>Alta</option>
                    <option value={4}>Crítica</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-iq-sub">
                    Categoría
                  </label>
                  <div className="pt-1.5">
                    <Etiqueta type="categoria" value={incidencia.categoria.name} />
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-2 flex items-center gap-2">
              <h3 className="text-sm font-semibold text-iq-text">Descripción</h3>
              {incidencia.tiempo_resolucion_minutos != null && (
                <span className="rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-600">
                  Resuelta en {formatResolution(incidencia.tiempo_resolucion_minutos)}
                </span>
              )}
            </div>
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-iq-body">
              {incidencia.descripcion}
            </p>
            {incidencia.notas && (
              <div className="mt-4 rounded-lg border border-iq-border bg-iq-hover p-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-iq-sub">
                  Notas
                </p>
                <p className="text-sm text-iq-body">{incidencia.notas}</p>
              </div>
            )}
          </div>

          <HistorialIncidencia items={incidencia.historial || []} />
        </div>

        <div className="space-y-6">
          <TarjetaAnalisisIA analisis={incidencia.analisis_ia} alConfirmar={confirmarAnalisis} />
          {(incidencia.estado.id !== ID_ESTADO_CERRADO || true) && (
            <div className="card p-5">
              <Boton
                variant="secondary"
                className="w-full"
                onClick={() => changeState(ID_ESTADO_CERRADO)}
                loading={savingState}
              >
                Marcar como resuelta
              </Boton>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}