import { useState } from "react";
import { Plus, LayoutGrid, List } from "lucide-react";
import { useIncidencias } from "../hooks/useIncidencias";
import { useNotificacion } from "../context/contextoNotificacion";
import { FiltrosIncidencias } from "../components/Incidencias/FiltrosIncidencias";
import { TablaIncidencias } from "../components/Incidencias/TablaIncidencias";
import { RejillaIncidencias } from "../components/Incidencias/RejillaIncidencias";
import { ModalIncidencia } from "../components/Incidencias/ModalIncidencia";
import { PaginacionIncidencias } from "../components/Incidencias/PaginacionIncidencias";
import { Spinner } from "../components/Common/Spinner";
import { cx } from "../utils/helpers";

export default function Incidencias() {
  const { filters, updateFilters, data, loading, createIncidencia } = useIncidencias();
  const { success } = useNotificacion();
  const [modalOpen, setModalOpen] = useState(false);
  const [view, setView] = useState("table");

  const handleCreate = async (payload) => {
    try {
      await createIncidencia(payload);
      success("Incidencia registrada correctamente");
    } catch (e) {
      throw e;
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-iq-border bg-white p-0.5">
            <button
              onClick={() => setView("table")}
              className={cx(
                "flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                view === "table" ? "bg-iq-primary/10 text-iq-primary" : "text-iq-sub hover:text-iq-text"
              )}
            >
              <List size={16} />
            </button>
            <button
              onClick={() => setView("grid")}
              className={cx(
                "flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                view === "grid" ? "bg-iq-primary/10 text-iq-primary" : "text-iq-sub hover:text-iq-text"
              )}
            >
              <LayoutGrid size={16} />
            </button>
          </div>
        </div>
        <button className="btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={16} />
          Nueva incidencia
        </button>
      </div>

      <FiltrosIncidencias filters={filters} onChange={updateFilters} />

      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Spinner size="lg" />
          </div>
        ) : (
          <div className="p-4">
            {view === "table" ? (
              <TablaIncidencias
                items={data.items}
                sortBy={filters.sort_by}
                order={filters.order}
                onSort={(sort_by, order) => updateFilters({ sort_by, order })}
                loading={loading}
              />
            ) : (
              <RejillaIncidencias items={data.items} loading={loading} />
            )}
            <div className="mt-4 border-t border-iq-border pt-4">
              <PaginacionIncidencias
                total={data.total}
                page={filters.page}
                pageSize={filters.pageSize}
                onChange={(page) => updateFilters({ page })}
              />
            </div>
          </div>
        )}
      </div>

      <ModalIncidencia
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}