/**
 * There is no analytics endpoint anywhere in this codebase — no router, no
 * use case, no schema. Rather than invent one (even a flagged, unconfirmed
 * one, as the Dashboard's placeholder approach did in Phase 3), Analytics
 * is built entirely on the ALREADY CONFIRMED /transactions and /categories
 * endpoints: fetch every transaction in the selected period, then compute
 * every number and chart client-side. Nothing here is guessed backend
 * behavior — it's arithmetic over real API responses.
 *
 * One backend rule IS replicated here deliberately, not invented: transfer
 * legs (transaction_type income/expense but transfer_id set) are excluded
 * from every total, exactly as the backend's own dashboard aggregation
 * queries do (see transaction_repository.py: "Transfer legs... are
 * EXCLUDED" appears on get_period_income_total, get_period_expense_total,
 * and get_top_expense_categories). A transfer between your own accounts
 * isn't income or spending, and this codebase already established that
 * rule server-side — Analytics just applies the same rule client-side.
 */

export const PERIODS = [
  { value: "7d", label: "7 Days", days: 7 },
  { value: "30d", label: "30 Days", days: 30 },
  { value: "3m", label: "3 Months", days: 90 },
  { value: "1y", label: "1 Year", days: 365 },
];

function toIsoDate(date) {
  return date.toISOString().slice(0, 10);
}

export function getPeriodRange(periodValue) {
  const period = PERIODS.find((p) => p.value === periodValue) || PERIODS[1];
  const to = new Date();
  const from = new Date();
  from.setDate(from.getDate() - (period.days - 1));
  return { dateFrom: toIsoDate(from), dateTo: toIsoDate(to), days: period.days };
}

/** Excludes transfer legs — see the module comment above for why. */
function excludeTransfers(transactions) {
  return transactions.filter((tx) => !tx.transfer_id);
}

export function computeTotals(transactions) {
  const real = excludeTransfers(transactions);
  const totalIncome = real
    .filter((tx) => tx.transaction_type === "income")
    .reduce((sum, tx) => sum + Number(tx.amount), 0);
  const totalExpenses = real
    .filter((tx) => tx.transaction_type === "expense")
    .reduce((sum, tx) => sum + Number(tx.amount), 0);
  const netSavings = totalIncome - totalExpenses;
  const savingsRate = totalIncome > 0 ? (netSavings / totalIncome) * 100 : null;
  return { totalIncome, totalExpenses, netSavings, savingsRate };
}

/**
 * Buckets expense/income totals by day (≤30 day periods), week (3 months),
 * or month (1 year) — fine enough granularity to be readable without
 * rendering 365 individual daily bars.
 */
export function bucketByTime(transactions, days) {
  const real = excludeTransfers(transactions);
  const granularity = days <= 30 ? "day" : days <= 90 ? "week" : "month";

  const bucketKey = (dateStr) => {
    const d = new Date(dateStr);
    if (granularity === "day") return toIsoDate(d);
    if (granularity === "month") return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    // week: ISO-ish — key by the Monday of that week
    const day = (d.getDay() + 6) % 7; // 0 = Monday
    const monday = new Date(d);
    monday.setDate(d.getDate() - day);
    return toIsoDate(monday);
  };

  const labelFor = (key) => {
    if (granularity === "month") {
      const [year, month] = key.split("-");
      return new Date(Number(year), Number(month) - 1, 1).toLocaleDateString(undefined, {
        month: "short",
      });
    }
    return new Date(key).toLocaleDateString(undefined, { month: "short", day: "numeric" });
  };

  const buckets = new Map();
  for (const tx of real) {
    const key = bucketKey(tx.date);
    if (!buckets.has(key)) buckets.set(key, { key, income: 0, expenses: 0 });
    const bucket = buckets.get(key);
    if (tx.transaction_type === "income") bucket.income += Number(tx.amount);
    else bucket.expenses += Number(tx.amount);
  }

  return [...buckets.values()]
    .sort((a, b) => (a.key < b.key ? -1 : 1))
    .map((b) => ({ label: labelFor(b.key), income: b.income, expenses: b.expenses }));
}

/** Expense-only breakdown by category, sorted descending by amount. */
export function aggregateByCategory(transactions, categoriesById) {
  const real = excludeTransfers(transactions).filter((tx) => tx.transaction_type === "expense");
  const totals = new Map();
  for (const tx of real) {
    const key = tx.category_id || "uncategorized";
    totals.set(key, (totals.get(key) || 0) + Number(tx.amount));
  }
  return [...totals.entries()]
    .map(([categoryId, amount]) => ({
      category_id: categoryId,
      category_name:
        categoryId === "uncategorized" ? "Uncategorized" : categoriesById.get(categoryId)?.name || "Uncategorized",
      amount,
    }))
    .sort((a, b) => b.amount - a.amount);
}
