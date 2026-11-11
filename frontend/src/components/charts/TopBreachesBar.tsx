import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export function TopBreachesBar({ data }: { data: { breach: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
        <XAxis type="number" allowDecimals={false} fontSize={12} />
        <YAxis dataKey="breach" type="category" fontSize={12} width={120} />
        <Tooltip />
        <Bar dataKey="total" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
