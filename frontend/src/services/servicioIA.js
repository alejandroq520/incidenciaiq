import api from "./api";

export const servicioIA = {
  preguntar: (pregunta) => api.post("/ia/preguntar", { pregunta }),
  perspectivas: (params = {}) => api.get("/ia/perspectivas", { params }),
  evaluacion: () => api.get("/ia/evaluacion"),
};