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

export function DesgloseCategorias({ data = [] }) {
  const sorted = [...data].sort((a, b) => a.total - b.total);
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={sorted} layout="vertical" margin={{ left: 8, right: 16 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
        <XAxis type="number" allowDecimals={false} stroke="#9CA3AF" fontSize={12} />
        <YAxis type="category" dataKey="name" width={64} stroke="#6B7280" fontSize={12} />
        <Tooltip
          cursor={{ fill: "#F9FAFB" }}
          formatter={(value) => [`${value} incidencias`, "Cantidad"]}
          contentStyle={{ borderRadius: 8, border: "1px solid #E5E7EB", fontSize: 12 }}
        />
        <Bar dataKey="total" radius={[0, 6, 6, 0]} barSize={20}>
          {sorted.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}