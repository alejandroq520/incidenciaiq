import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DisposicionPrincipal } from "./components/Layout/DisposicionPrincipal";
import { ProveedorNotificaciones } from "./context/contextoNotificacion";
import Dashboard from "./pages/Panel";
import Incidencias from "./pages/Incidencias";
import DetalleIncidencia from "./pages/DetalleIncidencia";
import Analitica from "./pages/Analitica";
import AyudaIA from "./pages/AyudaIA";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <ProveedorNotificaciones>
      <BrowserRouter>
        <Routes>
          <Route element={<DisposicionPrincipal />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidencias" element={<Incidencias />} />
            <Route path="/incidencias/:id" element={<DetalleIncidencia />} />
            <Route path="/analitica" element={<Analitica />} />
            <Route path="/ayuda-ia" element={<AyudaIA />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ProveedorNotificaciones>
  );
}