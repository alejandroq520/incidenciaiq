export const PRIORIDADES = [
  { id: 1, name: "Baja", level: 1, color: "#10B981", icon: "arrow-down" },
  { id: 2, name: "Media", level: 2, color: "#3B82F6", icon: "minus" },
  { id: 3, name: "Alta", level: 3, color: "#F97316", icon: "arrow-up" },
  { id: 4, name: "Crítica", level: 4, color: "#EF4444", icon: "alert-circle" },
];

export const prioridadById = (id) =>
  PRIORIDADES.find((p) => p.id === id) || PRIORIDADES[1];

export const prioridadByName = (name) =>
  PRIORIDADES.find((p) => p.name === name) || PRIORIDADES[1];