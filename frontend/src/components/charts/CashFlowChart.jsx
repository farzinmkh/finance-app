import {
  ResponsiveContainer,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Bar,
  Line,
  Tooltip,
  Legend,
} from "recharts";
import { Card } from "../ui/Card";
import { Skeleton } from "../ui/Skeleton";
import { EmptyState } from "../ui/EmptyState";
import { ChartTooltip } from "./ChartTooltip";
import { formatCurrency } from "../../utils/format";
import { BarChart3 } from "lucide-react";
import "./CashFlowChart.css";

/**
 * <CashFlowChart data={[{ label, income, expenses, balance }, ...]} loading empty />
 *
 * Colors are CSS variables (--color-income / --color-expense / --color-primary)
 * resolved live by the browser, so the chart re-colors automatically when
 * the theme toggles — no JS-side theme branching needed.
 */
export function CashFlowChart({ data, loading = false, empty = false }) {
  // Amounts may arrive as Decimal-as-string values from the API (see
  // services/dashboardService.js) — normalise to numbers for the chart only.
  const chartData = (data || []).map((point) => ({
    label: point.label,
    income: Number(point.income),
    expenses: Number(point.expenses),
    balance: Number(point.balance),
  }));

  return (
    <Card className="cash-flow-chart">
      <Card.Header title="Cash Flow" subtitle="Income, expenses, and balance over time" />

      {loading ? (
        <Skeleton height={280} radius="md" />
      ) : empty ? (
        <div className="cash-flow-chart__empty">
          <EmptyState
            icon={<BarChart3 size={22} />}
            title="No cash flow data yet"
            description="Once you add income and expenses, your trend appears here."
          />
        </div>
      ) : (
        <div className="cash-flow-chart__canvas">
          <ResponsiveContainer width="100%" height={280}>
            <ComposedChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="var(--color-border)" vertical={false} />
              <XAxis
                dataKey="label"
                stroke="var(--color-text-secondary)"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                tickLine={false}
                axisLine={{ stroke: "var(--color-border)" }}
              />
              <YAxis
                stroke="var(--color-text-secondary)"
                tick={{ fill: "var(--color-text-secondary)", fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                width={48}
                tickFormatter={(v) => formatCurrency(v, { signDisplay: "never" }).replace(/\.00$/, "")}
              />
              <Tooltip
                cursor={{ fill: "var(--color-surface-hover)" }}
                content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />}
              />
              <Legend
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ fontSize: 13, color: "var(--color-text-secondary)" }}
              />
              <Bar dataKey="income" name="Income" fill="var(--color-income)" radius={[4, 4, 0, 0]} maxBarSize={28} />
              <Bar dataKey="expenses" name="Expenses" fill="var(--color-expense)" radius={[4, 4, 0, 0]} maxBarSize={28} />
              <Line
                type="monotone"
                dataKey="balance"
                name="Balance"
                stroke="var(--color-primary)"
                strokeWidth={2}
                dot={{ r: 3, fill: "var(--color-primary)" }}
                activeDot={{ r: 5 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
