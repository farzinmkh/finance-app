import { apiFetch } from "./apiClient";

/**
 * UNCONFIRMED ROUTER — read before using.
 * ============================================================================
 * The request/response shapes below are NOT guessed — they come directly
 * from the real presentation/api/schemas/transfers.py file:
 *   CreateTransferRequest: { from_account_id, to_account_id, amount, date, notes? }
 *   TransferResponse: { id, from_account_id, to_account_id, amount, date, notes, created_at }
 *
 * What IS unconfirmed is whether a router actually mounts this schema.
 * TRANSACTIONS_ROUTER_SUMMARY.md — the most recent build log available —
 * lists "Transfers router (schema is now bug-fixed and ready to use)" under
 * "What's still pending". So this function calls the endpoint the schema
 * implies (`POST /transfers`, matching the /accounts, /categories,
 * /transactions pattern), but it may 404 until that router is built and
 * mounted. If it does, the app's existing ApiError/toast handling surfaces
 * that clearly — nothing here pretends the request succeeded.
 * ============================================================================
 */
export function createTransfer({ fromAccountId, toAccountId, amount, date, notes }) {
  return apiFetch("/transfers", {
    method: "POST",
    body: {
      from_account_id: fromAccountId,
      to_account_id: toAccountId,
      amount,
      date,
      notes: notes || null,
    },
  });
}
