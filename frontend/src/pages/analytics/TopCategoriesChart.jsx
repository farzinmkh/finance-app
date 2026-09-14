import { ResponsiveContainer, BarChart, Bar, Cell, XAxis, YAxis, Tooltip } from "recharts";
import { ListOrdered } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import { EmptyState } from "../../components/ui/EmptyState";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { formatCurrency } from "../../utils/format";
import "./TopCategoriesChart.css";

const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
];

/** `categories`: [{ category_name, amount }, ...], already sorted descending. */
export function TopCategoriesChart({ categories, loading, empty }) {
  const data = (categories || []).map((c, i) => ({
    name: c.category_name,
    value: c.amount,
    fill: PALETTE[i % PALETTE.length],
  }));
  const height = Math.max(160, data.length * 40);

  return (
    <Card className="top-categories-chart">
      <Card.Header title="Top Spending Categories" subtitle="Where most of your money went" />
      {loading ? (
        <Skeleton height={220} radius="md" />
      ) : empty || data.length === 0 ? (
        <div className="top-categories-chart__empty">
          <EmptyState icon={<ListOrdered size={22} />} title="No categorized expenses yet" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
            <XAxis
              type="number"
              hide
            />
            <YAxis
              type="category"
              dataKey="name"
              stroke="var(--color-text-secondary)"
              tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              width={100}
            />
            <Tooltip
              cursor={{ fill: "var(--color-surface-hover)" }}
              content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />}
            />
            <Bar dataKey="value" name="Amount" radius={[0, 4, 4, 0]} maxBarSize={22}>
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
