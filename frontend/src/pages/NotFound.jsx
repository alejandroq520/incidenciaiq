import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-iq-bg p-6 text-center">
      <p className="text-6xl font-bold text-iq-primary">404</p>
      <h1 className="text-2xl font-semibold text-iq-text">Página no encontrada</h1>
      <p className="max-w-md text-sm text-iq-sub">
        La página que buscas no existe o fue movida.
      </p>
      <Link to="/" className="btn-primary">
        Volver al dashboard
      </Link>
    </div>
  );
}