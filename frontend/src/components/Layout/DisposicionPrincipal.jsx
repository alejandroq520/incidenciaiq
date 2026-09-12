import { Outlet, useLocation } from "react-router-dom";
import { BarraLateral } from "./BarraLateral";
import { Header } from "./Header";

const TITLES = {
  "/": "Panel",
  "/incidencias": "Incidencias",
  "/analitica": "Analitica",
  "/ayuda-ia": "AI Help",
};

export function DisposicionPrincipal() {
  const { pathname } = useLocation();
  const titulo = pathname.startsWith("/incidencias/")
    ? "Detalle de incidencia"
    : TITLES[pathname] || "IncidenciaIQ";
  return (
    <div className="flex h-screen overflow-hidden bg-iq-bg">
      <BarraLateral />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header titulo={titulo} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}