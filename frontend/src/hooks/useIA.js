import { useCallback, useState } from "react";
import { servicioIA } from "../services/servicioIA";

export function useIA() {
  const [messages, setMessages] = useState([]);
  const [preguntando, setPreguntando] = useState(false);
  const [perspectivas, setPerspectivas] = useState([]);
  const [perspectivasLoading, setPerspectivasLoading] = useState(false);
  const [evaluacion, setEvaluacion] = useState(null);
  const [evaluacionLoading, setEvaluacionLoading] = useState(false);

  const preguntar = useCallback(async (pregunta) => {
    setPreguntando(true);
    const userMsg = { id: `u-${Date.now()}`, role: "user", content: pregunta };
    setMessages((prev) => [...prev, userMsg]);
    try {
      const result = await servicioIA.preguntar(pregunta);
      const aiMsg = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: result.respuesta,
      };
      setMessages((prev) => [...prev, aiMsg]);
      return aiMsg.content;
    } catch (e) {
      const errMsg = {
        id: `e-${Date.now()}`,
        role: "assistant",
        content: "No se pudo procesar la pregunta. Intenta de nuevo.",
        isError: true,
      };
      setMessages((prev) => [...prev, errMsg]);
      return errMsg.content;
    } finally {
      setPreguntando(false);
    }
  }, []);

  const cargarPerspectivas = useCallback(async (period = "7d") => {
    setPerspectivasLoading(true);
    try {
      const result = await servicioIA.perspectivas({ period, limit: 4 });
      setPerspectivas(result.perspectivas || []);
    } catch {
      setPerspectivas([]);
    } finally {
      setPerspectivasLoading(false);
    }
  }, []);

  const cargarEvaluacion = useCallback(async () => {
    setEvaluacionLoading(true);
    try {
      const result = await servicioIA.evaluacion();
      setEvaluacion(result);
    } catch {
      setEvaluacion(null);
    } finally {
      setEvaluacionLoading(false);
    }
  }, []);

  const clear = useCallback(() => setMessages([]), []);

  return {
    messages,
    preguntando,
    preguntar,
    perspectivas,
    cargarPerspectivas,
    perspectivasLoading,
    evaluacion,
    cargarEvaluacion,
    evaluacionLoading,
    clear,
  };
}