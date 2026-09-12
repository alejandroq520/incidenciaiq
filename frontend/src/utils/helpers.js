export function cx(...classes) {
  return classes.filter(Boolean).join(" ");
}

export function truncate(text, length = 80) {
  if (!text) return "";
  return text.length > length ? `${text.slice(0, length)}...` : text;
}