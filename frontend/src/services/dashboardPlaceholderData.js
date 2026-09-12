/**
 * ============================================================================
 *  TEMPORARY PLACEHOLDER DATA — NOT REAL, NOT PART OF SERVICE LOGIC
 * ============================================================================
 * The /dashboard endpoint's exact contract isn't confirmed yet (see the
 * comment in services/dashboardService.js). Nothing in that service file
 * returns fake data — it always makes a real request.
 *
 * This file exists ONLY so the Dashboard UI (cards, charts, transaction
 * list, responsive layout) can be built and reviewed before that endpoint
 * exists, without faking anything inside the service layer itself.
 *
 * How it's used: src/pages/dashboard/useDashboardSummary.js reads
 * VITE_USE_DASHBOARD_PLACEHOLDER from the environment. When it is not
 * explicitly set to "false", the hook returns this data instead of calling
 * the real API. Flip it to "false" in your .env once the endpoint is live —
 * the real request path (loading/error/empty handling included) is already
 * fully wired and will take over automatically.
 *
 * DELETE THIS FILE once the real endpoint is confirmed and the flag is
 * removed from .env.example.
 * ============================================================================
 */

export const dashboardPlaceholderData = {
  total_balance: "18420.35",
  accounts_count: 3,
  period: { date_from: "2026-09-01", date_to: "2026-09-30" },
  income: { amount: "5230.00", previous_amount: "4980.00", change_percent: 5.02 },
  expenses: { amount: "3184.42", previous_amount: "3420.10", change_percent: -6.89 },
  savings: { amount: "2045.58", rate_percent: 39.1 },
  cash_flow: [
    { label: "Apr", income: "4700", expenses: "3300", balance: "1400" },
    { label: "May", income: "4850", expenses: "3600", balance: "1250" },
    { label: "Jun", income: "4980", expenses: "3420", balance: "1560" },
    { label: "Jul", income: "5100", expenses: "3900", balance: "1200" },
    { label: "Aug", income: "4950", expenses: "3100", balance: "1850" },
    { label: "Sep", income: "5230", expenses: "3184", balance: "2046" },
  ],
  expense_breakdown: [
    { category_id: "1", category_name: "Housing", amount: "1200.00" },
    { category_id: "2", category_name: "Groceries", amount: "540.10" },
    { category_id: "3", category_name: "Transport", amount: "310.00" },
    { category_id: "4", category_name: "Dining out", amount: "420.32" },
    { category_id: "5", category_name: "Utilities", amount: "260.00" },
    { category_id: "6", category_name: "Other", amount: "454.00" },
  ],
  recent_transactions: [
    {
      id: "t1",
      description: "Whole Foods Market",
      category_name: "Groceries",
      category_type: "expense",
      transaction_type: "expense",
      date: "2026-09-10",
      amount: "86.42",
    },
    {
      id: "t2",
      description: "Monthly salary",
      category_name: "Salary",
      category_type: "income",
      transaction_type: "income",
      date: "2026-09-09",
      amount: "5230.00",
    },
    {
      id: "t3",
      description: "Uber ride",
      category_name: "Transport",
      category_type: "expense",
      transaction_type: "expense",
      date: "2026-09-08",
      amount: "18.75",
    },
    {
      id: "t4",
      description: "Electric bill",
      category_name: "Utilities",
      category_type: "expense",
      transaction_type: "expense",
      date: "2026-09-06",
      amount: "96.00",
    },
    {
      id: "t5",
      description: "Coffee with Sam",
      category_name: "Dining out",
      category_type: "expense",
      transaction_type: "expense",
      date: "2026-09-05",
      amount: "12.40",
    },
  ],
};
