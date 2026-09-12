import api from "./api";

export const servicioIncidencias = {
  list: (params = {}) => api.get("/incidencias", { params }),

  get: (id) => api.get(`/incidencias/${id}`),

  create: (data) => api.post("/incidencias", data),

  update: (id, data) => api.put(`/incidencias/${id}`, data),

  confirmarAnalisis: (id, isConfirmed = true) =>
    api.put(`/incidencias/${id}/analisis-ia/confirmar`, { confirmado: isConfirmed }),
};