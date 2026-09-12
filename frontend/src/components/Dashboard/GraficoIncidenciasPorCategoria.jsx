import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export function GraficoIncidenciasPorCategoria({ data = [] }) {
  if (!data.length) return null;
  const sorted = [...data].sort((a, b) => a.total - b.total);
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={sorted} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
        <XAxis
          type="number"
          allowDecimals={false}
          stroke="#9CA3AF"
          fontSize={12}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={64}
          stroke="#6B7280"
          fontSize={12}
        />
        <Tooltip
          cursor={{ fill: "#F9FAFB" }}
          formatter={(value) => [`${value} incidencias`, "Cantidad"]}
          contentStyle={{
            borderRadius: 8,
            border: "1px solid #E5E7EB",
            fontSize: 12,
          }}
        />
        <defs>
          <linearGradient id="catGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        <Bar dataKey="total" fill="url(#catGrad)" radius={[0, 6, 6, 0]} barSize={18}>
          {sorted.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}