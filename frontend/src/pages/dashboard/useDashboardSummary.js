import { useCallback, useEffect, useState } from "react";
import { getDashboardSummary } from "../../services/dashboardService";
import { dashboardPlaceholderData } from "../../services/dashboardPlaceholderData";

const USE_PLACEHOLDER = import.meta.env.VITE_USE_DASHBOARD_PLACEHOLDER !== "false";

function isEmptySummary(data) {
  if (!data) return true;
  const noBalance = !data.total_balance || Number(data.total_balance) === 0;
  const noActivity = !data.recent_transactions?.length && !data.cash_flow?.length;
  return noBalance && noActivity && data.accounts_count === 0;
}

/**
 * Loads dashboard data and exposes a single `status` so the page and each
 * section can render loading/empty/error consistently:
 *
 *   status: "loading" | "error" | "empty" | "success"
 *
 * While VITE_USE_DASHBOARD_PLACEHOLDER is not "false" (see .env.example),
 * this resolves with isolated sample data instead of calling the real
 * endpoint — see services/dashboardPlaceholderData.js for why.
 */
export function useDashboardSummary() {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  const load = useCallback(async () => {
    setState({ status: "loading", data: null, error: null });
    try {
      const data = USE_PLACEHOLDER
        ? await new Promise((resolve) => setTimeout(() => resolve(dashboardPlaceholderData), 500))
        : await getDashboardSummary();

      setState({
        status: isEmptySummary(data) ? "empty" : "success",
        data,
        error: null,
      });
    } catch (err) {
      setState({ status: "error", data: null, error: err });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, usingPlaceholder: USE_PLACEHOLDER, refetch: load };
}
