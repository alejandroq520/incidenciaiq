import { useState } from "react";
import { Send } from "lucide-react";

export function EntradaIA({ alEnviar, disabled }) {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    alEnviar(text);
    setValue("");
  };

  return (
    <div className="focused-grow flex items-end gap-2 rounded-xl border border-iq-border bg-white p-3 shadow-card">
      <textarea
        rows={1}
        className="max-h-32 flex-1 resize-none bg-transparent px-1 py-1 text-sm text-iq-text outline-none placeholder-iq-sub"
        placeholder="Pregúntale al sistema... (ej: ¿Cuántas incidencias críticas están abiertas?)"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
      />
      <button
        onClick={submit}
        disabled={disabled || !value.trim()}
        className="btn-primary !rounded-lg !px-3 !py-2"
        aria-label="Enviar pregunta"
      >
        <Send size={16} />
      </button>
    </div>
  );
}