export function EstadoVacio({ icon: Icon, titulo, descripcion, accion }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      {Icon && (
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-iq-hover text-iq-sub">
          <Icon size={26} />
        </div>
      )}
      <h4 className="text-sm font-semibold text-iq-text">{titulo}</h4>
      {descripcion && <p className="max-w-sm text-sm text-iq-sub">{descripcion}</p>}
      {accion}
    </div>
  );
}