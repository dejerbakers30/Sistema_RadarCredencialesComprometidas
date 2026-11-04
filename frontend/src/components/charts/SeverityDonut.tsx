import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";

const COLORS: Record<string, string> = {
  baja: "#10b981",
  media: "#f59e0b",
  alta: "#f97316",
  critica: "#dc2626",
};

export function SeverityDonut({ data }: { data: { severidad: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <PieChart>
        <Pie data={data} dataKey="total" nameKey="severidad" innerRadius={60} outerRadius={90}>
          {data.map((d) => (
            <Cell key={d.severidad} fill={COLORS[d.severidad] ?? "#94a3b8"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
