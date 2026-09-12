import { useState } from "react";
import { useAnalitica } from "../hooks/useAnalitica";
import { ResumenMetricas } from "../components/Analitica/ResumenMetricas";
import { GraficoTendencia } from "../components/Analitica/GraficoTendencia";
import { DesgloseCategorias } from "../components/Analitica/DesgloseCategorias";
import { TablaCategorias } from "../components/Analitica/TablaCategorias";
import { Spinner } from "../components/Common/Spinner";
import { cx } from "../utils/helpers";

const PERIODS = [
  { value: "7d", label: "Últimos 7 días" },
  { value: "30d", label: "Últimos 30 días" },
  { value: "90d", label: "Último trimestre" },
];

export default function Analitica() {
  const [period, setPeriod] = useState("30d");
  const [custom, setCustom] = useState({ from: "", to: "" });
  const { metrics, porCategoria, trend, resolution, loading, load } = useAnalitica(period);

  const applyCustom = async () => {
    if (!custom.from || !custom.to) return;
    const extra = { date_from: `${custom.from}T00:00:00`, date_to: `${custom.to}T23:59:59` };
    setPeriod("custom");
    await load("custom", extra);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={cx(
                "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
                period === p.value
                  ? "border-iq-primary bg-iq-primary/10 text-iq-primary"
                  : "border-iq-border bg-white text-iq-body hover:bg-iq-hover"
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            type="date"
            className="input !w-auto"
            value={custom.from}
            onChange={(e) => setCustom({ ...custom, from: e.target.value })}
          />
          <span className="text-sm text-iq-sub">→</span>
          <input
            type="date"
            className="input !w-auto"
            value={custom.to}
            onChange={(e) => setCustom({ ...custom, to: e.target.value })}
          />
          <button
            className="btn-primary"
            onClick={applyCustom}
            disabled={!custom.from || !custom.to}
          >
            Aplicar
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex h-[50vh] items-center justify-center">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <ResumenMetricas metrics={metrics} />

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div className="card p-5">
              <h3 className="mb-4 text-base font-semibold text-iq-text">
                Evolución de incidencias en el tiempo
              </h3>
              <GraficoTendencia data={trend} />
            </div>
            <div className="card p-5">
              <h3 className="mb-4 text-base font-semibold text-iq-text">
                Distribución por categoría
              </h3>
              <DesgloseCategorias data={porCategoria} />
            </div>
          </div>

          <div className="card">
            <div className="border-b border-iq-border px-5 py-4">
              <h3 className="text-base font-semibold text-iq-text">
                Incidencias por categoría (detalle)
              </h3>
            </div>
            <div className="p-4">
              <TablaCategorias
                data={porCategoria}
                resolutionPorCategoria={resolution?.por_categoria || []}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}