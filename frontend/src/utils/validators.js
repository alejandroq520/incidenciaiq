export function validateIncidencia({ titulo, descripcion, categoria_id, prioridad_id }) {
  const errors = {};
  if (!titulo || titulo.trim().length < 5) {
    errors.titulo = "El título debe tener al menos 5 caracteres";
  }
  if (!descripcion || descripcion.trim().length < 10) {
    errors.descripcion = "La descripción debe tener al menos 10 caracteres";
  }
  if (!categoria_id) errors.categoria_id = "Selecciona una categoría";
  if (!prioridad_id) errors.prioridad_id = "Selecciona una prioridad";
  return errors;
}