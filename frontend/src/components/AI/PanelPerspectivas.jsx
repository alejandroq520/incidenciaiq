import { Spinner } from "../Common/Spinner";

const IMPACT_STYLES = {
  high: "border-red-100 bg-red-50",
  medium: "border-orange-100 bg-orange-50",
  low: "border-blue-100 bg-blue-50",
  positive: "border-green-100 bg-green-50",
};

export function PanelPerspectivas({ perspectivas = [], loading }) {
  return (
    <div className="card p-5">
      <h3 className="mb-4 flex items-center gap-2 text-base font-semibold text-iq-text">
        Perspectivas de la IA
      </h3>
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Spinner />
        </div>
      ) : perspectivas.length ? (
        <div className="space-y-3">
          {perspectivas.map((ins) => (
            <div
              key={ins.id}
              className={`cursor-pointer rounded-lg border p-3 transition-shadow hover:shadow-card ${IMPACT_STYLES[ins.impact] || IMPACT_STYLES.medium}`}
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-iq-text">
                  {ins.titulo}
                </p>
              </div>
              {ins.categoria && (
                <span className="mb-1.5 inline-block rounded-full bg-white/70 px-2 py-0.5 text-xs font-medium text-iq-body">
                  {ins.categoria}
                </span>
              )}
              <p className="text-xs leading-relaxed text-iq-body">{ins.descripcion}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-iq-sub">Cargando perspectivas...</p>
      )}
    </div>
  );
}