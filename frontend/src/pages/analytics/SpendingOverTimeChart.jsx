import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts";
import { TrendingUp } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import { EmptyState } from "../../components/ui/EmptyState";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { formatCurrency } from "../../utils/format";
import "./SpendingOverTimeChart.css";

/**
 * `data`: [{ label, income, expenses }, ...] — pre-bucketed by
 * utils/analyticsAggregation.js's bucketByTime (day/week/month depending on
 * the selected period, so a 1-year view isn't 365 illegible points).
 */
export function SpendingOverTimeChart({ data, loading, empty }) {
  return (
    <Card className="spending-over-time">
      <Card.Header title="Spending Over Time" subtitle="Income and expenses across the period" />
      {loading ? (
        <Skeleton height={260} radius="md" />
      ) : empty ? (
        <div className="spending-over-time__empty">
          <EmptyState icon={<TrendingUp size={22} />} title="Not enough data yet" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="var(--color-border)" vertical={false} />
            <XAxis
              dataKey="label"
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "var(--color-border)" }}
              minTickGap={20}
            />
            <YAxis
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              width={48}
              tickFormatter={(v) => formatCurrency(v, { signDisplay: "never" }).replace(/\.00$/, "")}
            />
            <Tooltip content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 13, color: "var(--color-text-secondary)" }}
            />
            <Line
              type="monotone"
              dataKey="income"
              name="Income"
              stroke="var(--color-income)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="expenses"
              name="Expenses"
              stroke="var(--color-expense)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
