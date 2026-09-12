import { NavLink } from "react-router-dom";
import { LayoutDashboard, Boxes, BarChart3, Bot, Activity } from "lucide-react";
import { cx } from "../../utils/helpers";

const NAV = [
  { to: "/", label: "Panel", icon: LayoutDashboard, end: true },
  { to: "/incidencias", label: "Incidencias", icon: Boxes },
  { to: "/analitica", label: "Analitica", icon: BarChart3 },
  { to: "/ayuda-ia", label: "AI Help", icon: Bot },
];

export function BarraLateral() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-iq-border bg-white md:flex">
      <div className="flex h-16 items-center gap-2.5 border-b border-iq-border px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-iq-primary text-white">
          <Activity size={20} />
        </div>
        <div className="flex flex-col">
          <span className="text-base font-bold leading-none text-iq-text">IncidenciaIQ</span>
          <span className="text-xs text-iq-sub">Monitor inteligente</span>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                isActive
                  ? "bg-iq-primary/10 text-iq-primary"
                  : "text-iq-body hover:bg-iq-hover hover:text-iq-text"
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-iq-border p-4">
        <div className="rounded-lg bg-iq-hover p-3">
          <p className="text-xs font-semibold text-iq-text">Entorno</p>
          <p className="text-xs text-iq-sub">Desarrollo · v1.0.0</p>
        </div>
      </div>
    </aside>
  );
}