import { Gauge, Target, ShieldCheck, Layers } from "lucide-react";
import { Spinner } from "../Common/Spinner";

const SOURCE_LABELS = {
  openai: "IA",
  heuristic: "Reglas",
  case: "Caso similar",
  openai_case: "IA + caso",
  heuristic_case: "Reglas + caso",
};

function MiniStat({ icon: Icon, label, value, accent = "text-iq-primary", sub }) {
  return (
    <div className="rounded-lg border border-iq-border bg-white p-3">
      <div className="flex items-center gap-2">
        <Icon size={16} className={accent} />
        <p className="text-xs font-medium text-iq-sub">{label}</p>
      </div>
      <p className="mt-1 text-lg font-bold text-iq-text">{value}</p>
      {sub && <p className="text-xs text-iq-sub">{sub}</p>}
    </div>
  );
}

export function EvaluacionClasificador({ evaluacion, loading }) {
  return (
    <div className="card p-5">
      <h3 className="mb-4 flex items-center gap-2 text-base font-semibold text-iq-text">
        <Gauge size={16} className="text-iq-primary" />
        Evaluación del clasificador
        <span className="text-xs font-normal text-iq-sub">
          (datos reales contra categorías asignadas/confirmadas)
        </span>
      </h3>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Spinner />
        </div>
      ) : !evaluacion ? (
        <p className="text-sm text-iq-sub">No hay datos de evaluación todavía.</p>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MiniStat
              icon={Target}
              label="Precisión"
              value={`${(evaluacion.precision * 100).toFixed(1)}%`}
              accent={
                evaluacion.precision >= 0.7 ? "text-iq-success" : "text-red-500"
              }
              sub={`${evaluacion.aciertos} correctos / ${evaluacion.errores} incorrectos`}
            />
            <MiniStat
              icon={Layers}
              label="Casos evaluados"
              value={evaluacion.evaluados}
              sub={`con análisis sobre ${evaluacion.total_incidencias} incidencias`}
            />
            <MiniStat
              icon={ShieldCheck}
              label="Confirmados"
              value={evaluacion.confirmados}
              sub={
                evaluacion.confirmados > 0
                  ? `${(evaluacion.precision_confirmada * 100).toFixed(0)}% precisión`
                  : "confirma en el detalle"
              }
            />
            <MiniStat
              icon={Gauge}
              label="Cobertura"
              value={`${(evaluacion.cobertura * 100).toFixed(1)}%`}
              sub="incidencias con análisis IA"
            />
          </div>

          <div>
            <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-iq-sub">
              Precisión por origen
            </p>
            <div className="flex flex-wrap gap-2">
              {evaluacion.por_fuente.map((row) => (
                <span
                  key={row.group}
                  className="rounded-full border border-iq-border bg-iq-hover px-3 py-1 text-xs font-medium text-iq-body"
                >
                  {SOURCE_LABELS[row.group] || row.group}:{" "}
                  <span className="font-bold text-iq-text">
                    {(row.precision * 100).toFixed(0)}%
                  </span>{" "}
                  ({row.aciertos}/{row.evaluados})
                </span>
              ))}
              {!evaluacion.por_fuente.length && (
                <span className="text-sm text-iq-sub">Sin evaluaciones aún.</span>
              )}
            </div>
          </div>

          {evaluacion.por_categoria.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-iq-border bg-gray-50/50">
                    <th className="table-th">Categoría real</th>
                    <th className="table-th">Evaluados</th>
                    <th className="table-th">Aciertos</th>
                    <th className="table-th">Precisión</th>
                  </tr>
                </thead>
                <tbody>
                  {evaluacion.por_categoria.map((row) => (
                    <tr key={row.group} className="border-b border-iq-border last:border-0">
                      <td className="table-td font-medium text-iq-text">{row.group}</td>
                      <td className="table-td">{row.evaluados}</td>
                      <td className="table-td">{row.aciertos}</td>
                      <td className="table-td">
                        <span
                          className={`font-semibold ${
                            row.precision >= 0.7 ? "text-iq-success" : "text-red-500"
                          }`}
                        >
                          {(row.precision * 100).toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}