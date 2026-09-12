import { createContext, useCallback, useContext, useRef, useState } from "react";
import { Toast } from "../components/Common/Toast";

const contextoNotificacion = createContext(null);

export function ProveedorNotificaciones({ children }) {
  const [toasts, setToasts] = useState([]);
  const counter = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const notify = useCallback(
    (message, type = "info", duration = 4000) => {
      const id = ++counter.current;
      setToasts((prev) => [...prev, { id, message, type }]);
      if (duration) {
        setTimeout(() => dismiss(id), duration);
      }
      return id;
    },
    [dismiss]
  );

  const success = useCallback((m) => notify(m, "success"), [notify]);
  const error = useCallback((m) => notify(m, "error"), [notify]);
  const info = useCallback((m) => notify(m, "info"), [notify]);
  const warning = useCallback((m) => notify(m, "warning"), [notify]);

  return (
    <contextoNotificacion.Provider value={{ notify, success, error, info, warning }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
        {toasts.map((t) => (
          <Toast
            key={t.id}
            message={t.message}
            type={t.type}
            onDismiss={() => dismiss(t.id)}
          />
        ))}
      </div>
    </contextoNotificacion.Provider>
  );
}

export function useNotificacion() {
  const ctx = useContext(contextoNotificacion);
  if (!ctx) throw new Error("useNotificacion must be used within ProveedorNotificaciones");
  return ctx;
}