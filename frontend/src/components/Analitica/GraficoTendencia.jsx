import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export function GraficoTendencia({ data = [] }) {
  const clean = data.map((d) => ({
    ...d,
    label: d.date.includes("T") ? d.date.slice(11, 16) : d.date.slice(5),
  }));
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={clean} margin={{ top: 8, right: 16, bottom: 0, left: -12 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="label" stroke="#9CA3AF" fontSize={12} />
        <YAxis allowDecimals={false} stroke="#9CA3AF" fontSize={12} />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: "1px solid #E5E7EB", fontSize: 12 }}
          labelFormatter={(_, payload) => {
            const p = payload?.[0]?.payload;
            return p?.date || "";
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line
          type="monotone"
          dataKey="created"
          name="Creadas"
          stroke="#3B82F6"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
        <Line
          type="monotone"
          dataKey="closed"
          name="Cerradas"
          stroke="#10B981"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}