import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { PieChart as PieChartIcon } from "lucide-react";
import { Card } from "../ui/Card";
import { Skeleton } from "../ui/Skeleton";
import { EmptyState } from "../ui/EmptyState";
import { ChartTooltip } from "./ChartTooltip";
import { formatCurrency } from "../../utils/format";
import "./ExpenseDonutChart.css";

const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
];

/**
 * <ExpenseDonutChart data={[{ category_id, category_name, amount }, ...]} loading empty />
 * `amount` may be a Decimal-as-string from the API; converted to Number here
 * for the chart only (display purposes, not arithmetic).
 */
export function ExpenseDonutChart({
  data,
  loading = false,
  empty = false,
  title = "Expense Breakdown",
  subtitle = "Where your money went this period",
}) {
  const chartData = (data || []).map((item, index) => ({
    name: item.category_name,
    value: Number(item.amount),
    color: PALETTE[index % PALETTE.length],
  }));
  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card className="expense-donut">
      <Card.Header title={title} subtitle={subtitle} />

      {loading ? (
        <div className="expense-donut__loading">
          <Skeleton width={180} height={180} radius="full" />
        </div>
      ) : empty ? (
        <div className="expense-donut__empty">
          <EmptyState
            icon={<PieChartIcon size={22} />}
            title="No expenses recorded"
            description="Categorized expenses will show up here as a breakdown."
          />
        </div>
      ) : (
        <div className="expense-donut__body">
          <div className="expense-donut__canvas">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius="62%"
                  outerRadius="90%"
                  paddingAngle={2}
                  stroke="var(--color-surface)"
                  strokeWidth={2}
                >
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="expense-donut__center">
              <span className="text-caption">Total</span>
              <span className="text-card-title text-mono">{formatCurrency(total)}</span>
            </div>
          </div>

          <ul className="expense-donut__legend">
            {chartData.map((entry) => (
              <li key={entry.name} className="expense-donut__legend-item">
                <span className="expense-donut__legend-swatch" style={{ backgroundColor: entry.color }} />
                <span className="expense-donut__legend-name text-secondary">{entry.name}</span>
                <span className="expense-donut__legend-value text-label text-mono">
                  {formatCurrency(entry.value)}
                </span>
                <span className="expense-donut__legend-percent text-caption">
                  {total > 0 ? Math.round((entry.value / total) * 100) : 0}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
