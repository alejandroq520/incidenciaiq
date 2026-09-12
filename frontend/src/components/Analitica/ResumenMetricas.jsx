import { CheckCircle2, Clock3, ShieldCheck, Repeat } from "lucide-react";
import { TarjetaKPI } from "../Common/TarjetaKPI";

export function ResumenMetricas({ metrics }) {
  if (!metrics) return null;
  const cmp = metrics.comparison || {};
  const avgChange =
    parseInt(cmp.resolution_time_change_minutes) > 0
      ? `+${cmp.resolution_time_change_minutes} min`
      : `${cmp.resolution_time_change_minutes ?? 0} min`;

  const slaColor =
    metrics.sla_compliance_percentage >= 90
      ? "success"
      : metrics.sla_compliance_percentage >= 70
        ? "warning"
        : "danger";

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <TarjetaKPI
        label="Resueltas"
        value={metrics.closed_incidencias}
        change={`${cmp.closed_incidencias_trend === "up" ? "+" : ""}${metrics.closed_incidencias} en el periodo`}
        icon={CheckCircle2}
        color="success"
      />
      <TarjetaKPI
        label="Tiempo promedio de resolución"
        value={`${metrics.average_resolution_time_hours}h`}
        change={`${avgChange} respecto al periodo anterior`}
        icon={Clock3}
        color="primary"
      />
      <TarjetaKPI
        label="SLA compliance"
        value={`${metrics.sla_compliance_percentage}%`}
        change="Objetivo: 8 horas"
        icon={ShieldCheck}
        color={slaColor}
      />
      <TarjetaKPI
        label="Patrones detectados"
        value={metrics.recurring_patterns}
        change="categorías recurrentes"
        icon={Repeat}
        color="warning"
      />
    </div>
  );
}