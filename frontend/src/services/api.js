import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      (Array.isArray(error.response?.data?.detail)
        ? error.response.data.detail[0]?.msg
        : null) ||
      "Error de conexión con el servidor";
    return Promise.reject(new Error(message));
  }
);

export default api;