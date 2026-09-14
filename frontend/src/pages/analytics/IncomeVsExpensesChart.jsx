import { ResponsiveContainer, BarChart, Bar, Cell, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { Scale } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import { EmptyState } from "../../components/ui/EmptyState";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { formatCurrency } from "../../utils/format";
import "./IncomeVsExpensesChart.css";

export function IncomeVsExpensesChart({ totalIncome, totalExpenses, loading, empty }) {
  const data = [
    { name: "Income", value: totalIncome, fill: "var(--color-income)" },
    { name: "Expenses", value: totalExpenses, fill: "var(--color-expense)" },
  ];

  return (
    <Card className="income-vs-expenses">
      <Card.Header title="Income vs Expenses" subtitle="Totals for the selected period" />
      {loading ? (
        <Skeleton height={200} radius="md" />
      ) : empty ? (
        <div className="income-vs-expenses__empty">
          <EmptyState icon={<Scale size={22} />} title="No activity in this period" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
            <CartesianGrid stroke="var(--color-border)" horizontal={false} />
            <XAxis
              type="number"
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "var(--color-border)" }}
              tickFormatter={(v) => formatCurrency(v, { signDisplay: "never" }).replace(/\.00$/, "")}
            />
            <YAxis
              type="category"
              dataKey="name"
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 13 }}
              tickLine={false}
              axisLine={false}
              width={70}
            />
            <Tooltip
              cursor={{ fill: "var(--color-surface-hover)" }}
              content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={36}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
