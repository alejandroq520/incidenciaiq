export function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("es-PE", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDateShort(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("es-PE", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function timeAgo(iso) {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));
  const units = [
    ["año", 31536000],
    ["mes", 2592000],
    ["semana", 604800],
    ["día", 86400],
    ["hora", 3600],
    ["minuto", 60],
  ];
  for (const [name, value] of units) {
    const count = Math.floor(seconds / value);
    if (count >= 1) {
      const plural = count === 1 ? name : `${name}s`;
      return `hace ${count} ${plural}`;
    }
  }
  return "hace un momento";
}

export function formatResolution(minutes) {
  if (minutes == null) return "—";
  const hours = minutes / 60;
  if (hours < 1) return `${Math.round(minutes)} min`;
  return `${hours.toFixed(1)}h`;
}

export function formatNumber(value) {
  return new Intl.NumberFormat("es-PE").format(value ?? 0);
}

export function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Buenos días";
  if (h < 19) return "Buenas tardes";
  return "Buenas noches";
}