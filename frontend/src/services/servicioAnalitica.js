import api from "./api";

export const servicioAnalitica = {
  metrics: (params = {}) => api.get("/analitica/metricas", { params }),
  porCategoria: (params = {}) => api.get("/analitica/por-categoria", { params }),
  trend: (params = {}) => api.get("/analitica/tendencia", { params }),
  resolutionTime: (params = {}) =>
    api.get("/analitica/tiempo-resolucion", { params }),
};