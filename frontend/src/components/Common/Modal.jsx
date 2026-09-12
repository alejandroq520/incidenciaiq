import { X } from "lucide-react";

export function Modal({ isOpen, onClose, titulo, children, maxWidth = "max-w-lg" }) {
  if (!isOpen) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 p-4 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className={`card w-full ${maxWidth} animate-slide-up`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-iq-border px-6 py-4">
          <h3 className="text-base font-semibold text-iq-text">{titulo}</h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-iq-sub transition-colors hover:bg-iq-hover hover:text-iq-text"
            aria-label="Cerrar"
          >
            <X size={18} />
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}