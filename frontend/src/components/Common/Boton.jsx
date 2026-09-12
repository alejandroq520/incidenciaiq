import { cx } from "../../utils/helpers";
import { Spinner } from "./Spinner";

export function Boton({
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  className = "",
  children,
  ...rest
}) {
  const classes = {
    primary: "btn-primary",
    secondary: "btn-secondary",
    danger: "btn-danger",
  }[variant];

  const sizes = {
    sm: "!px-3 !py-1.5 !text-xs",
    md: "",
    lg: "!px-6 !py-2.5 !text-base",
  }[size];

  return (
    <button
      className={cx(classes, sizes, className)}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <Spinner size="sm" light={variant !== "secondary"} />}
      {children}
    </button>
  );
}