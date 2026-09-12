import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, AlertTriangle, FolderOpen, ArrowRight } from "lucide-react";
import { servicioAnalitica } from "../services/servicioAnalitica";
import { servicioIncidencias } from "../services/servicioIncidencias";
import { TarjetaKPI } from "../components/Common/TarjetaKPI";
import { GraficoIncidenciasPorCategoria } from "../components/Dashboard/GraficoIncidenciasPorCategoria";
import { GraficoDistribucionEstados } from "../components/Dashboard/GraficoDistribucionEstados";
import { TablaIncidenciasRecientes } from "../components/Dashboard/TablaIncidenciasRecientes";
import { greeting } from "../utils/formatters";
import { ROUTES } from "../constants/rutas";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [porCategoria, setPorCategoria] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [m, b, r] = await Promise.all([
          servicioAnalitica.metrics({ period: "30d" }),
          servicioAnalitica.porCategoria({ period: "30d" }),
          servicioIncidencias.list({ limit: 5, sort_by: "creado_en", order: "desc" }),
        ]);
        if (!active) return;
        setMetrics(m);
        setPorCategoria(b.categorias || []);
        setRecent(r.items || []);
      } catch {
        /* empty */
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="skeleton h-7 w-64" />
          <div className="skeleton h-4 w-48" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="skeleton h-32" />
          <div className="skeleton h-32" />
          <div className="skeleton h-32" />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="skeleton h-72" />
          <div className="skeleton h-72" />
        </div>
        <div className="skeleton h-72" />
      </div>
    );
  }

  const total = metrics?.total_incidencias ?? 0;
  const opened = metrics?.opened_incidencias ?? 0;
  const critical = metrics?.critical_incidencias ?? 0;
  const closed = metrics?.closed_incidencias ?? 0;
  const pending = Math.max(0, total - opened - closed);
  const cmp = metrics?.comparison || {};

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-iq-text">
          {greeting()}, Alejandro
        </h2>
        <p className="text-sm text-iq-sub">Resumen operativo de incidencias</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <TarjetaKPI
          label="Total de incidencias"
          value={total}
          change={`+${cmp.total_incidencias_change_percent ?? 0}% este periodo`}
          icon={FolderOpen}
          color="gray"
        />
        <TarjetaKPI
          label="Incidencias abiertas"
          value={opened}
          change={`+${opened} sin resolver`}
          icon={Activity}
          color="warning"
        />
        <TarjetaKPI
          label="Incidencias críticas"
          value={critical}
          change={`${critical} requieren atención`}
          icon={AlertTriangle}
          color="danger"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-base font-semibold text-iq-text">
              Incidencias por categoría
            </h3>
            <Link
              to={ROUTES.analitica}
              className="flex items-center gap-1 text-xs font-medium text-iq-primary hover:underline"
            >
              Ver analitica <ArrowRight size={12} />
            </Link>
          </div>
          <GraficoIncidenciasPorCategoria data={porCategoria} />
        </div>
        <div className="card p-5">
          <h3 className="mb-2 text-base font-semibold text-iq-text">
            Distribución por estado
          </h3>
          <GraficoDistribucionEstados open={opened} closed={closed} pending={pending} />
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between border-b border-iq-border px-5 py-4">
          <h3 className="text-base font-semibold text-iq-text">Últimas incidencias</h3>
          <Link
            to={ROUTES.incidencias}
            className="flex items-center gap-1 text-xs font-medium text-iq-primary hover:underline"
          >
            Ver todas <ArrowRight size={12} />
          </Link>
        </div>
        <TablaIncidenciasRecientes items={recent} />
      </div>
    </div>
  );
}