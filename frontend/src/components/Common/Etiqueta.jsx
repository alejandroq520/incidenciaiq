import { cx } from "../../utils/helpers";

const STYLES = {
  estado: {
    Abierta: "bg-red-50 text-red-600 border-red-100",
    Pendiente: "bg-amber-50 text-amber-600 border-amber-100",
    Cerrada: "bg-green-50 text-green-600 border-green-100",
  },
  prioridad: {
    Critica: "bg-red-50 text-red-600 border-red-100",
    "Crítica": "bg-red-50 text-red-600 border-red-100",
    Alta: "bg-orange-50 text-orange-600 border-orange-100",
    Media: "bg-blue-50 text-blue-600 border-blue-100",
    Baja: "bg-gray-50 text-gray-500 border-gray-200",
  },
  categoria: {
    Acceso: "bg-red-50 text-red-600 border-red-100",
    Pagos: "bg-amber-50 text-amber-600 border-amber-100",
    Sistema: "bg-blue-50 text-blue-600 border-blue-100",
    Red: "bg-violet-50 text-violet-600 border-violet-100",
    Otros: "bg-gray-50 text-gray-500 border-gray-200",
  },
  default: "bg-gray-50 text-gray-600 border-gray-200",
};

export function Etiqueta({ type = "default", value, color, dot }) {
  const style = (type === "prioridad" ? STYLES.prioridad[value?.replace("í", "i")] : STYLES[type]?.[value]) || STYLES.default;
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        style
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {value}
    </span>
  );
}