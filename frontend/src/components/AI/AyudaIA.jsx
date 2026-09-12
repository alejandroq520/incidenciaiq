import { Bot, User } from "lucide-react";
import { Spinner } from "../Common/Spinner";
import { cx } from "../../utils/helpers";

function Markdown({ text }) {
  const parts = String(text || "").split(/\n/);
  return (
    <div className="space-y-2">
      {parts.map((line, i) => {
        const trimmed = line.trim();
        if (trimmed.startsWith("- ")) {
          return <li key={i} className="ml-4 list-disc">…{trimmed.slice(2)}</li>;
        }
        const bold = trimmed.split(/\*\*(.+?)\*\*/g);
        if (bold.length > 1) {
          return (
            <p key={i}>
              {bold.map((part, j) =>
                j % 2 === 1 ? (
                  <strong key={j}>{part}</strong>
                ) : (
                  <span key={j}>{part}</span>
                )
              )}
            </p>
          );
        }
        if (trimmed.startsWith("**") && trimmed.endsWith("**")) {
          return <p key={i}><strong>{trimmed.slice(2, -2)}</strong></p>;
        }
        return <p key={i}>{trimmed}</p>;
      })}
    </div>
  );
}

export function AyudaIA({ messages = [], preguntando, suggested, onSelect }) {
  const hasMessages = messages.length > 0;
  return (
    <div className="card flex h-[420px] flex-col overflow-hidden">
      <div className="flex-1 space-y-4 overflow-y-auto bg-iq-bg/60 p-4">
        {!hasMessages && (
          <div className="space-y-2 p-2">
            <p className="text-center text-sm text-iq-sub">
              Haz preguntas sobre tus incidencias. El sistema analizará los datos y
              te proporcionará perspectivas automáticas.
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              {suggested.map((q) => (
                <button
                  key={q}
                  onClick={() => onSelect(q)}
                  className="rounded-lg border border-iq-border bg-white px-3 py-2.5 text-left text-sm text-iq-body transition-all duration-150 hover:border-iq-primary hover:bg-blue-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={cx("flex items-start gap-2.5 animate-slide-up", m.role === "user" ? "justify-end" : "justify-start")}
          >
            {m.role === "assistant" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-iq-primary text-white">
                <Bot size={16} />
              </div>
            )}
            <div
              className={cx(
                "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm",
                m.role === "user"
                  ? "rounded-br-sm bg-iq-primary text-white"
                  : m.isError
                    ? "rounded-bl-sm border border-red-100 bg-red-50 text-red-600"
                    : "rounded-bl-sm border border-iq-border bg-white text-iq-text"
              )}
            >
              {m.role === "user" ? m.content : <Markdown text={m.content} />}
            </div>
            {m.role === "user" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-iq-hover text-iq-sub">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        {preguntando && (
          <div className="flex items-start gap-2.5">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-iq-primary text-white">
              <Bot size={16} />
            </div>
            <div className="flex items-center gap-2 rounded-2xl rounded-bl-sm border border-iq-border bg-white px-4 py-3">
              <Spinner size="sm" />
              <span className="text-sm text-iq-sub">Analizando datos...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}