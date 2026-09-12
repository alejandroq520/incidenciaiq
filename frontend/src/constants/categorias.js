export const CATEGORIAS = [
  { id: 1, name: "Acceso", color: "#EF4444", icon: "lock-open" },
  { id: 2, name: "Pagos", color: "#F59E0B", icon: "credit-card" },
  { id: 3, name: "Sistema", color: "#3B82F6", icon: "server" },
  { id: 4, name: "Red", color: "#8B5CF6", icon: "wifi-off" },
  { id: 5, name: "Otros", color: "#6B7280", icon: "help-circle" },
];

export const categoriaById = (id) =>
  CATEGORIAS.find((c) => c.id === id) || CATEGORIAS[4];

export const categoriaByName = (name) =>
  CATEGORIAS.find((c) => c.name === name) || CATEGORIAS[4];