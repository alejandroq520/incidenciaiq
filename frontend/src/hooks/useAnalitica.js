import { useEffect, useState } from "react";
import { servicioAnalitica } from "../services/servicioAnalitica";

export function useAnalitica(period = "7d") {
  const [metrics, setMetrics] = useState(null);
  const [porCategoria, setPorCategoria] = useState([]);
  const [trend, setTrend] = useState([]);
  const [resolution, setResolution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAll = (p, extra = {}) => {
    setLoading(true);
    setError(null);
    return Promise.all([
      servicioAnalitica.metrics({ period: p, ...extra }),
      servicioAnalitica.porCategoria({ period: p, ...extra }),
      servicioAnalitica.trend({ period: p, ...extra }),
      servicioAnalitica.resolutionTime({ period: p, ...extra }),
    ])
      .then(([m, b, t, r]) => {
        setMetrics(m);
        setPorCategoria(b.categorias || []);
        setTrend(t.data || []);
        setResolution(r);
        setError(null);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const load = async (p = period, extra = {}) => {
    await fetchAll(p, extra);
  };

  useEffect(() => {
    fetchAll(period);
  }, [period]);

  return { metrics, porCategoria, trend, resolution, loading, error, load };
}