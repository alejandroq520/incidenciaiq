import { useEffect, useState } from "react";
import { Modal } from "../Common/Modal";
import { Boton } from "../Common/Boton";
import { CATEGORIAS } from "../../constants/categorias";
import { PRIORIDADES } from "../../constants/prioridades";
import { validateIncidencia } from "../../utils/validators";

export function ModalIncidencia({ isOpen, onClose, onSubmit }) {
  const [form, setForm] = useState({ titulo: "", descripcion: "", categoria_id: "", prioridad_id: "" });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setForm({ titulo: "", descripcion: "", categoria_id: "", prioridad_id: "" });
      setErrors({});
      setSubmitting(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const v = validateIncidencia(form);
    setErrors(v);
    if (Object.keys(v).length) return;
    setSubmitting(true);
    try {
      await onSubmit({
        titulo: form.titulo.trim(),
        descripcion: form.descripcion.trim(),
        categoria_id: Number(form.categoria_id),
        prioridad_id: Number(form.prioridad_id),
        creado_por: "Alejandro",
      });
      onClose();
    } catch (err) {
      setErrors({ general: err.message });
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} titulo="Nueva incidencia" maxWidth="max-w-[600px]">
      <form onSubmit={handleSubmit} className="space-y-4">
        {errors.general && (
          <p className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-600">
            {errors.general}
          </p>
        )}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-iq-text">Título</label>
          <input
            className="input"
            placeholder="Ej: Error de acceso al sistema"
            maxLength={120}
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
            disabled={submitting}
          />
          {errors.titulo && <p className="mt-1 text-xs text-red-500">{errors.titulo}</p>}
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-iq-text">Descripción</label>
          <textarea
            className="input min-h-[110px] resize-y"
            placeholder="Describe el problema con detalle..."
            maxLength={1000}
            value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            disabled={submitting}
          />
          {errors.descripcion && (
            <p className="mt-1 text-xs text-red-500">{errors.descripcion}</p>
          )}
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-iq-text">Categoría</label>
            <select
              className="select"
              value={form.categoria_id}
              onChange={(e) => setForm({ ...form, categoria_id: e.target.value })}
              disabled={submitting}
            >
              <option value="">Seleccionar...</option>
              {CATEGORIAS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            {errors.categoria_id && <p className="mt-1 text-xs text-red-500">{errors.categoria_id}</p>}
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-iq-text">Prioridad</label>
            <select
              className="select"
              value={form.prioridad_id}
              onChange={(e) => setForm({ ...form, prioridad_id: e.target.value })}
              disabled={submitting}
            >
              <option value="">Seleccionar...</option>
              {PRIORIDADES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            {errors.prioridad_id && <p className="mt-1 text-xs text-red-500">{errors.prioridad_id}</p>}
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Boton variant="secondary" type="button" onClick={onClose} disabled={submitting}>
            Cancelar
          </Boton>
          <Boton type="submit" loading={submitting}>
            Registrar
          </Boton>
        </div>
      </form>
    </Modal>
  );
}