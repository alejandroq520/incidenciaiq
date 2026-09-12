import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from "lucide-react";
import { cx } from "../../utils/helpers";

const CONFIG = {
  success: { icon: CheckCircle2, classes: "border-green-100 bg-green-50 text-green-700", iconColor: "text-green-500" },
  error: { icon: AlertCircle, classes: "border-red-100 bg-red-50 text-red-700", iconColor: "text-red-500" },
  info: { icon: Info, classes: "border-blue-100 bg-blue-50 text-blue-700", iconColor: "text-blue-500" },
  warning: { icon: AlertTriangle, classes: "border-amber-100 bg-amber-50 text-amber-700", iconColor: "text-amber-500" },
};

export function Toast({ message, type = "info", onDismiss }) {
  const cfg = CONFIG[type] || CONFIG.info;
  const Icon = cfg.icon;
  return (
    <div
      className={cx(
        "pointer-events-auto flex items-center gap-3 rounded-xl border px-4 py-3 shadow-card animate-slide-in-right",
        cfg.classes
      )}
    >
      <Icon size={18} className={cx("shrink-0", cfg.iconColor)} />
      <p className="text-sm font-medium">{message}</p>
      <button
        onClick={onDismiss}
        className="ml-2 shrink-0 rounded p-0.5 opacity-60 transition-opacity hover:opacity-100"
        aria-label="Cerrar notificación"
      >
        <X size={14} />
      </button>
    </div>
  );
}