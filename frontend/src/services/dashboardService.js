import { apiFetch } from "./apiClient";

/**
 * Dashboard API contract — NOT YET CONFIRMED against a real router.
 * ==================================================================
 * The backend's transaction repository already exposes the aggregation
 * queries a dashboard needs (get_period_income_total, get_period_expense_total,
 * get_top_expense_categories, list_recent — see transaction_repository.py),
 * and account balances are summable from GET /accounts. What is NOT in this
 * codebase yet is the router/schema that composes them into one response.
 *
 * This function calls the endpoint shape that composition would most
 * naturally produce. Nothing here is invented business logic — it is a thin
 * fetch, isolated in one place, so that once the real dashboard router
 * exists you only need to adjust the path/response-mapping below.
 *
 * Assumed contract:
 *   GET /dashboard?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
 *   -> {
 *        total_balance: "12345.6700",       // sum of all account balances (Decimal-as-string)
 *        accounts_count: 3,
 *        period: { date_from, date_to },
 *        income:   { amount: "...", previous_amount: "..."|null, change_percent: number|null },
 *        expenses: { amount: "...", previous_amount: "..."|null, change_percent: number|null },
 *        savings:  { amount: "...", rate_percent: number|null },
 *        cash_flow: [ { label: "Apr", income: "...", expenses: "...", balance: "..." }, ... ],
 *        expense_breakdown: [ { category_id, category_name, amount: "..." }, ... ],
 *        recent_transactions: [
 *          { id, description, category_name, category_type, transaction_type, date, amount: "..." }, ...
 *        ],
 *      }
 */
export function getDashboardSummary({ dateFrom, dateTo } = {}) {
  const params = new URLSearchParams();
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  const query = params.toString();
  return apiFetch(`/dashboard${query ? `?${query}` : ""}`);
}
