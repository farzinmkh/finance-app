import { useState } from "react";
import { Wallet, TrendingUp, TrendingDown, PiggyBank } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/Button";
import { ErrorState } from "../components/ui/ErrorState";
import { StatCard } from "../components/dashboard/StatCard";
import { ExpenseDonutChart } from "../components/charts/ExpenseDonutChart";
import { PeriodSelector } from "./analytics/PeriodSelector";
import { IncomeVsExpensesChart } from "./analytics/IncomeVsExpensesChart";
import { SpendingOverTimeChart } from "./analytics/SpendingOverTimeChart";
import { TopCategoriesChart } from "./analytics/TopCategoriesChart";
import { TopCategoriesList } from "./analytics/TopCategoriesList";
import { useAnalyticsData } from "./analytics/useAnalyticsData";
import { formatCurrency, formatPercent } from "../utils/format";
import { usePreferences } from "../hooks/usePreferences";
import "./Analytics.css";

export default function Analytics() {
  const [period, setPeriod] = useState("30d");
  const { status, data, refetch } = useAnalyticsData(period);
  const { currency } = usePreferences();

  const loading = status === "loading";
  const empty = status === "empty";
  const totals = data?.totals || { totalIncome: 0, totalExpenses: 0, netSavings: 0, savingsRate: null };

  return (
    <PageContainer>
      <div className="analytics__header">
        <h1 className="text-page-title">Analytics</h1>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {status === "error" && (
        <ErrorState
          title="Couldn't load analytics"
          description="Check your connection and try again."
          action={<Button onClick={refetch}>Retry</Button>}
        />
      )}

      {status !== "error" && (
        <>
          <div className="analytics__stats">
            <StatCard
              icon={Wallet}
              tone="primary"
              title="Total Income"
              loading={loading}
              amount={!loading && formatCurrency(totals.totalIncome, { currency })}
              secondary={!loading && "Selected period"}
            />
            <StatCard
              icon={TrendingDown}
              tone="expense"
              title="Total Expenses"
              loading={loading}
              amount={!loading && formatCurrency(totals.totalExpenses, { currency })}
              secondary={!loading && "Selected period"}
            />
            <StatCard
              icon={TrendingUp}
              tone="income"
              title="Net Savings"
              loading={loading}
              amount={!loading && formatCurrency(totals.netSavings, { currency })}
              secondary={!loading && "Income minus expenses"}
            />
            <StatCard
              icon={PiggyBank}
              tone="warning"
              title="Savings Rate"
              loading={loading}
              amount={!loading && (totals.savingsRate === null ? "—" : formatPercent(totals.savingsRate))}
              secondary={!loading && "Of total income"}
            />
          </div>

          <div className="analytics__full-chart">
            <SpendingOverTimeChart data={data?.timeSeries || []} loading={loading} empty={empty} />
          </div>

          <div className="analytics__chart-pair">
            <IncomeVsExpensesChart
              totalIncome={totals.totalIncome}
              totalExpenses={totals.totalExpenses}
              loading={loading}
              empty={empty}
            />
            <ExpenseDonutChart
              data={data?.categoryBreakdown || []}
              loading={loading}
              empty={empty}
              title="Expenses by Category"
              subtitle="Share of spending per category"
            />
          </div>

          <div className="analytics__chart-pair">
            <TopCategoriesChart categories={data?.topCategories || []} loading={loading} empty={empty} />
            <TopCategoriesList categories={data?.topCategories || []} loading={loading} empty={empty} />
          </div>
        </>
      )}
    </PageContainer>
  );
}
