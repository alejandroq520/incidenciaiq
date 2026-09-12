import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

export function GraficoDistribucionEstados({ open = 0, closed = 0, pending = 0 }) {
  const data = [
    { name: "Abiertas", value: open, color: "#EF4444" },
    { name: "Cerradas", value: closed, color: "#10B981" },
    { name: "Pendientes", value: pending, color: "#F59E0B" },
  ].filter((d) => d.value > 0);

  const total = open + closed + pending;

  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            strokeWidth={2}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name) => [
              `${value} (${total ? ((value / total) * 100).toFixed(1) : 0}%)`,
              name,
            ]}
            contentStyle={{
              borderRadius: 8,
              border: "1px solid #E5E7EB",
              fontSize: 12,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-4">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-2 text-sm">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: d.color }} />
            <span className="text-iq-body">
              {d.name}{" "}
              <span className="font-semibold text-iq-text">
                {total ? ((d.value / total) * 100).toFixed(1) : 0}%
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}