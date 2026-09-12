import { useCallback, useEffect, useState } from "react";
import { servicioIncidencias } from "../services/servicioIncidencias";

const DEFAULT_FILTERS = {
  estado_ids: [],
  prioridad_ids: [],
  categoria_ids: [],
  date_from: "",
  date_to: "",
  search: "",
  sort_by: "creado_en",
  order: "desc",
  page: 1,
  pageSize: 20,
};

function toParams(f) {
  const params = {
    skip: (f.page - 1) * f.pageSize,
    limit: f.pageSize,
    sort_by: f.sort_by,
    order: f.order,
  };
  if (f.search?.trim()) params.search = f.search.trim();
  if (f.estado_ids.length) params.estado_id = f.estado_ids.join(",");
  if (f.prioridad_ids.length) params.prioridad_id = f.prioridad_ids.join(",");
  if (f.categoria_ids.length) params.categoria_id = f.categoria_ids.join(",");
  if (f.date_from) params.date_from = f.date_from;
  if (f.date_to) params.date_to = f.date_to;
  return params;
}

export function useIncidencias() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async (next = filters) => {
    setLoading(true);
    setError(null);
    try {
      const result = await servicioIncidencias.list(toParams(next));
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filters);
  }, [load]);

  const updateFilters = useCallback(
    (patch) => {
      const next = { ...filters, ...patch };
      setFilters(next);
      load(next);
    },
    [filters, load]
  );

  const refresh = useCallback(() => load(filters), [filters, load]);

  const createIncidencia = useCallback(
    async (payload) => {
      await servicioIncidencias.create(payload);
      await refresh();
    },
    [refresh]
  );

  return { filters, setFilters, updateFilters, data, loading, error, refresh, createIncidencia };
}