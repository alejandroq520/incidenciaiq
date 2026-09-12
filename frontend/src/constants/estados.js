export const ESTADOS = [
  { id: 1, name: "Abierta", color: "#EF4444" },
  { id: 2, name: "Pendiente", color: "#F59E0B" },
  { id: 3, name: "Cerrada", color: "#10B981" },
];

export const estadoPorId = (id) => ESTADOS.find((s) => s.id === id) || ESTADOS[0];

export const estadoPorNombre = (name) =>
  ESTADOS.find((s) => s.name === name) || ESTADOS[0];

export const ID_ESTADO_CERRADO = 3;