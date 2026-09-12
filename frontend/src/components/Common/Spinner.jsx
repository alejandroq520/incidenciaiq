import { cx } from "../../utils/helpers";

const SIZES = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-[3px]",
};

export function Spinner({ size = "md", light = false, className = "" }) {
  return (
    <span
      className={cx(
        "inline-block animate-spin rounded-full border-t-transparent",
        SIZES[size],
        light ? "border-white" : "border-iq-primary",
        className
      )}
      aria-label="Cargando"
    />
  );
}