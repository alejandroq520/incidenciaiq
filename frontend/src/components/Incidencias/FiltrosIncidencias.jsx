import { Search, FilterX } from "lucide-react";
import { ESTADOS } from "../../constants/estados";
import { PRIORIDADES } from "../../constants/prioridades";
import { CATEGORIAS } from "../../constants/categorias";
import { cx } from "../../utils/helpers";

function ChipGroup({ label, options, selected, onToggle }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-semibold uppercase tracking-wide text-iq-sub">
        {label}
      </span>
      <div className="flex flex-wrap gap-1.5">
        {options.map((opt) => {
          const active = selected.includes(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onToggle(opt.value)}
              className={cx(
                "rounded-full border px-3 py-1 text-xs font-medium transition-all duration-150",
                active
                  ? "border-iq-primary bg-iq-primary/10 text-iq-primary"
                  : "border-iq-border bg-white text-iq-body hover:bg-iq-hover"
              )}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function FiltrosIncidencias({ filters, onChange }) {
  const toggle = (key, value) => {
    const list = filters[key].includes(value)
      ? filters[key].filter((v) => v !== value)
      : [...filters[key], value];
    onChange({ [key]: list, page: 1 });
  };

  const hasFilters =
    filters.estado_ids.length ||
    filters.prioridad_ids.length ||
    filters.categoria_ids.length ||
    filters.date_from ||
    filters.date_to ||
    filters.search;

  return (
    <div className="card p-4 space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-[220px] flex-1">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-iq-sub"
          />
          <input
            className="input !pl-9"
            placeholder="Buscar por título o descripción..."
            value={filters.search}
            onChange={(e) => onChange({ search: e.target.value, page: 1 })}
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-iq-sub">Desde:</label>
          <input
            type="date"
            className="input !w-auto"
            value={filters.date_from}
            onChange={(e) => onChange({ date_from: e.target.value, page: 1 })}
          />
          <label className="text-xs text-iq-sub">Hasta:</label>
          <input
            type="date"
            className="input !w-auto"
            value={filters.date_to}
            onChange={(e) => onChange({ date_to: e.target.value, page: 1 })}
          />
        </div>
        {hasFilters && (
          <button
            onClick={() =>
              onChange({
                estado_ids: [],
                prioridad_ids: [],
                categoria_ids: [],
                date_from: "",
                date_to: "",
                search: "",
                page: 1,
              })
            }
            className="btn-secondary !px-3"
            title="Limpiar filtros"
          >
            <FilterX size={16} />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <ChipGroup
          label="Estado"
          options={ESTADOS.map((s) => ({ label: s.name, value: s.id }))}
          selected={filters.estado_ids}
          onToggle={(v) => toggle("estado_ids", v)}
        />
        <ChipGroup
          label="Prioridad"
          options={PRIORIDADES.map((p) => ({ label: p.name, value: p.id }))}
          selected={filters.prioridad_ids}
          onToggle={(v) => toggle("prioridad_ids", v)}
        />
        <ChipGroup
          label="Categoría"
          options={CATEGORIAS.map((c) => ({ label: c.name, value: c.id }))}
          selected={filters.categoria_ids}
          onToggle={(v) => toggle("categoria_ids", v)}
        />
      </div>
    </div>
  );
}