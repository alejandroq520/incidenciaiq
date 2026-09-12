import { useEffect } from "react";
import { useIA } from "../hooks/useIA";
import { AyudaIA } from "../components/AI/AyudaIA";
import { EntradaIA } from "../components/AI/EntradaIA";
import { PanelPerspectivas } from "../components/AI/PanelPerspectivas";
import { EvaluacionClasificador } from "../components/AI/EvaluacionClasificador";

const SUGGESTED = [
  "¿Cuántas incidencias críticas están abiertas?",
  "¿Cuál es la categoría con más incidencias?",
  "Resume las incidencias de esta semana",
  "¿Cuál fue el tiempo promedio de resolución?",
];

export default function PaginaAyudaIA() {
  const {
    messages,
    preguntando,
    preguntar,
    perspectivas,
    cargarPerspectivas,
    perspectivasLoading,
    evaluacion,
    cargarEvaluacion,
    evaluacionLoading,
  } = useIA();

  useEffect(() => {
    cargarPerspectivas("30d");
    cargarEvaluacion();
  }, [cargarPerspectivas, cargarEvaluacion]);

  return (
    <div className="space-y-6">
      <p className="text-sm text-iq-sub">
        Haz preguntas sobre tus incidencias. El sistema analizará los datos y te
        proporcionará perspectivas automáticas.
      </p>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <AyudaIA
            messages={messages}
            preguntando={preguntando}
            suggested={SUGGESTED}
            onSelect={(q) => preguntar(q)}
          />
          <EntradaIA alEnviar={preguntar} disabled={preguntando} />
        </div>
        <PanelPerspectivas perspectivas={perspectivas} loading={perspectivasLoading} />
      </div>

      <EvaluacionClasificador evaluacion={evaluacion} loading={evaluacionLoading} />
    </div>
  );
}