import { useCallback, useEffect, useState } from "react";
import { listTransactions } from "../../services/transactionService";
import { listCategories } from "../../services/categoryService";
import {
  getPeriodRange,
  computeTotals,
  bucketByTime,
  aggregateByCategory,
} from "../../utils/analyticsAggregation";

// Safety cap on how many pages to pull for one period. At 200/page this is
// 2,000 transactions — comfortably beyond a year of realistic personal
// finance activity — so this only ever protects against a pathological
// account, never trims a normal one.
const MAX_PAGES = 10;
const PAGE_SIZE = 200;

async function fetchAllTransactions({ dateFrom, dateTo }) {
  const first = await listTransactions({ page: 1, pageSize: PAGE_SIZE, dateFrom, dateTo });
  const items = [...first.items];
  const totalPages = Math.min(first.total_pages, MAX_PAGES);
  for (let page = 2; page <= totalPages; page += 1) {
    const next = await listTransactions({ page, pageSize: PAGE_SIZE, dateFrom, dateTo });
    items.push(...next.items);
  }
  return items;
}

export function useAnalyticsData(period) {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, status: "loading", error: null }));
    try {
      const { dateFrom, dateTo, days } = getPeriodRange(period);
      const [transactions, categories] = await Promise.all([
        fetchAllTransactions({ dateFrom, dateTo }),
        listCategories(),
      ]);
      const categoriesById = new Map(categories.map((c) => [c.id, c]));

      const totals = computeTotals(transactions);
      const timeSeries = bucketByTime(transactions, days);
      const categoryBreakdown = aggregateByCategory(transactions, categoriesById);
      const topCategories = categoryBreakdown.slice(0, 6).map((c) => ({
        ...c,
        percentage: totals.totalExpenses > 0 ? (c.amount / totals.totalExpenses) * 100 : 0,
      }));

      const isEmpty = transactions.length === 0;

      setState({
        status: isEmpty ? "empty" : "success",
        data: { totals, timeSeries, categoryBreakdown, topCategories, dateFrom, dateTo },
        error: null,
      });
    } catch (error) {
      setState({ status: "error", data: null, error });
    }
  }, [period]);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, refetch: load };
}
