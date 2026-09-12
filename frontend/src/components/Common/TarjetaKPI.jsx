import { TrendingUp } from "lucide-react";
import { cx } from "../../utils/helpers";

export function TarjetaKPI({ label, value, change, icon: Icon, color = "gray", trend }) {
  const palettes = {
    gray: "bg-gray-50 text-gray-500",
    warning: "bg-orange-50 text-orange-500",
    danger: "bg-red-50 text-red-500",
    success: "bg-green-50 text-green-500",
    primary: "bg-blue-50 text-blue-500",
  };
  const trendColors = {
    up: "text-red-500",
    up_green: "text-green-500",
    down: "text-blue-500",
    positive: "text-green-500",
  };
  const letter = change || "";
  const trendStyle =
    String(letter).includes("-") || String(letter).toLowerCase().includes("mejor")
      ? "down"
      : String(letter).toLowerCase().includes("crí") || String(letter).toLowerCase().includes("aumento") || /\+\d/.test(letter)
        ? "up"
        : "positive";

  return (
    <div className="card p-5 animate-slide-up">
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <p className="text-xs font-medium uppercase tracking-wide text-iq-sub">{label}</p>
          <p className="text-[36px] font-bold leading-none text-iq-text">{value}</p>
          {change && (
            <p
              className={cx(
                "mt-2 flex items-center gap-1 text-xs font-medium",
                trendColors[trendStyle]
              )}
            >
              {!String(change).startsWith("-") && <TrendingUp size={12} />}
              {change}
            </p>
          )}
        </div>
        {Icon && (
          <div
            className={cx(
              "flex h-11 w-11 items-center justify-center rounded-lg",
              palettes[color]
            )}
          >
            <Icon size={22} />
          </div>
        )}
      </div>
    </div>
  );
}