import { Link } from "react-router-dom";
import { Check, Tags } from "lucide-react";
import { useState } from "react";
import { Boton } from "../Common/Boton";
import { Etiqueta } from "../Common/Etiqueta";

function Section({ titulo, children }) {
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-iq-sub">
        {titulo}
      </p>
      {children}
    </div>
  );
}

const SOURCE_LABELS = {
  openai: { label: "IA", cls: "border-purple-100 bg-purple-50 text-purple-700" },
  heuristic: { label: "Reglas", cls: "border-gray-200 bg-gray-50 text-gray-600" },
  case: { label: "Caso similar", cls: "border-orange-100 bg-orange-50 text-orange-700" },
  openai_case: { label: "IA + Caso similar", cls: "border-indigo-100 bg-indigo-50 text-indigo-700" },
  heuristic_case: { label: "Reglas + Caso", cls: "border-teal-100 bg-teal-50 text-teal-700" },
};

export function TarjetaAnalisisIA({ analisis, alConfirmar }) {
  const [confirmando, setConfirmando] = useState(false);

  if (!analisis) {
    return (
      <div className="card p-5">
        <h3 className="mb-2 flex items-center gap-2 text-base font-semibold text-iq-text">
          Análisis IA
        </h3>
        <p className="text-sm text-iq-sub">
          No hay análisis IA disponible para esta incidencia.
        </p>
      </div>
    );
  }

  const fuente = SOURCE_LABELS[analisis.fuente] || {
    label: analisis.fuente || "Reglas",
    cls: "border-gray-200 bg-gray-50 text-gray-600",
  };

  const manejarConfirmacion = async () => {
    setConfirmando(true);
    try {
      await alConfirmar();
    } finally {
      setConfirmando(false);
    }
  };

  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-base font-semibold text-iq-text">
          Análisis IA
        </h3>
        <div className="flex items-center justify-end gap-2">
          <span
            className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${fuente.cls}`}
          >
            {fuente.label}
          </span>
          {analisis.confianza != null && (
            <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-600">
              Confianza {Math.round(analisis.confianza * 100)}%
            </span>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Section titulo="Categoría sugerida">
            <Etiqueta type="categoria" value={analisis.categoria_sugerida || "—"} />
          </Section>
          <Section titulo="Prioridad sugerida">
            <Etiqueta type="prioridad" value={analisis.prioridad_sugerida || "—"} />
          </Section>
        </div>

        {analisis.justificacion && (
          <div className="rounded-lg border border-iq-border bg-iq-hover p-3">
            <p className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-iq-sub">
              <Tags size={12} /> ¿Por qué esta sugerencia?
            </p>
            <p className="text-sm text-iq-body">{analisis.justificacion}</p>
            {analisis.incidencia_referencia_id && (
              <Link
                to={`/incidencias/${analisis.incidencia_referencia_id}`}
                className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-iq-primary hover:underline"
              >
                Ver caso histórico INC-{analisis.incidencia_referencia_id}
                {analisis.indice_similitud != null && (
                  <span className="font-normal text-iq-sub">
                    · similitud {Math.round(analisis.indice_similitud * 100)}%
                  </span>
                )}
              </Link>
            )}
          </div>
        )}

        <Section titulo="Resumen automático">
          <p className="text-sm leading-relaxed text-iq-body">
            {analisis.resumen || "Sin resumen disponible."}
          </p>
        </Section>
        <Section titulo="Recomendación">
          <p className="text-sm leading-relaxed text-iq-body">
            {analisis.recomendacion || "Sin recomendación disponible."}
          </p>
        </Section>

        {analisis.confirmado ? (
          <div className="flex items-center gap-2 rounded-lg border border-green-100 bg-green-50 px-3 py-2 text-sm font-medium text-green-600">
            <Check size={16} />
            Clasificación confirmada
          </div>
        ) : (
          <Boton
            variant="secondary"
            className="w-full"
            loading={confirmando}
            onClick={manejarConfirmacion}
          >
            <Check size={16} />
            Confirmar clasificación
          </Boton>
        )}
      </div>
    </div>
  );
}