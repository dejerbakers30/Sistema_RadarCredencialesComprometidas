import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export function ResetsStackedBar({ data }: { data: { resultado: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <BarChart data={data}>
        <XAxis dataKey="resultado" fontSize={12} />
        <YAxis fontSize={12} allowDecimals={false} />
        <Tooltip />
        <Legend />
        <Bar dataKey="total" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
