import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { format, parseISO } from "date-fns";

export function TrendLine({ data }: { data: { fecha: string; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={256}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="fecha"
          tickFormatter={(v) => format(parseISO(v), "dd/MM")}
          fontSize={12}
        />
        <YAxis fontSize={12} allowDecimals={false} />
        <Tooltip
          labelFormatter={(v) => format(parseISO(v as string), "dd/MM/yyyy")}
          formatter={(value) => [value, "Filtraciones"]}
        />
        <Line type="monotone" dataKey="total" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
