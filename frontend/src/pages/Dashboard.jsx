import { Wallet, TrendingUp, TrendingDown, PiggyBank, Inbox } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { StatCard } from "../components/dashboard/StatCard";
import { RecentTransactions } from "../components/dashboard/RecentTransactions";
import { CashFlowChart } from "../components/charts/CashFlowChart";
import { ExpenseDonutChart } from "../components/charts/ExpenseDonutChart";
import { DashboardHeader } from "./dashboard/DashboardHeader";
import { useDashboardSummary } from "./dashboard/useDashboardSummary";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { formatCurrency, formatPercent } from "../utils/format";
import "./Dashboard.css";

/**
 * Builds a StatCard `trend` prop from a change_percent value.
 * `invert` flips color semantics for metrics where "up" is unfavorable
 * (e.g. rising expenses) — see StatCard.jsx for why direction and color
 * are tracked independently.
 */
function buildTrend(changePercent, { invert = false } = {}) {
  if (changePercent === null || changePercent === undefined) return null;
  const direction = changePercent >= 0 ? "up" : "down";
  const positive = invert ? changePercent < 0 : changePercent >= 0;
  return {
    direction,
    positive,
    label: `${formatPercent(Math.abs(changePercent))} vs last month`,
  };
}

export default function Dashboard() {
  const { status, data, usingPlaceholder, refetch } = useDashboardSummary();

  const loading = status === "loading";

  if (status === "error") {
    return (
      <PageContainer>
        <DashboardHeader />
        <ErrorState
          title="Couldn't load your dashboard"
          description="Check your connection and try again."
          action={<Button onClick={refetch}>Retry</Button>}
        />
      </PageContainer>
    );
  }

  if (status === "empty") {
    return (
      <PageContainer>
        <DashboardHeader />
        <EmptyState
          icon={<Inbox size={22} />}
          title="Nothing to show yet"
          description="Add an account and record a transaction to see your financial overview here."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <DashboardHeader />

      {usingPlaceholder && (
        <Badge tone="warning" className="dashboard__placeholder-badge">
          Showing sample data — connect the dashboard endpoint to see your real numbers
        </Badge>
      )}

      <div className="dashboard__stats">
        <StatCard
          icon={Wallet}
          tone="primary"
          title="Total Balance"
          loading={loading}
          amount={!loading && formatCurrency(data.total_balance)}
          secondary={
            !loading &&
            `${data.accounts_count} account${data.accounts_count === 1 ? "" : "s"}`
          }
        />
        <StatCard
          icon={TrendingUp}
          tone="income"
          title="Income"
          loading={loading}
          amount={!loading && formatCurrency(data.income.amount)}
          secondary={!loading && "This period"}
          trend={!loading ? buildTrend(data.income.change_percent) : null}
        />
        <StatCard
          icon={TrendingDown}
          tone="expense"
          title="Expenses"
          loading={loading}
          amount={!loading && formatCurrency(data.expenses.amount)}
          secondary={!loading && "This period"}
          trend={!loading ? buildTrend(data.expenses.change_percent, { invert: true }) : null}
        />
        <StatCard
          icon={PiggyBank}
          tone="warning"
          title="Savings"
          loading={loading}
          amount={!loading && formatCurrency(data.savings.amount)}
          secondary={
            !loading &&
            data.savings.rate_percent !== null &&
            `${formatPercent(data.savings.rate_percent)} savings rate`
          }
        />
      </div>

      <div className="dashboard__charts">
        <CashFlowChart
          data={!loading ? data.cash_flow : []}
          loading={loading}
          empty={!loading && data.cash_flow.length === 0}
        />
        <ExpenseDonutChart
          data={!loading ? data.expense_breakdown : []}
          loading={loading}
          empty={!loading && data.expense_breakdown.length === 0}
        />
      </div>

      <RecentTransactions
        items={!loading ? data.recent_transactions : []}
        loading={loading}
        empty={!loading && data.recent_transactions.length === 0}
      />
    </PageContainer>
  );
}
