import { apiFetch } from "./apiClient";

/**
 * Confirmed contract — accounts.py (schema) + PHASE1/2 memory confirm the
 * router is mounted at /api/v1/accounts. AccountResponse:
 *   { id, name, account_type, currency, opening_balance, current_balance, created_at }
 * (opening_balance / current_balance are Decimal-as-string.)
 */

export function listAccounts() {
  return apiFetch("/accounts");
}

export function getAccount(accountId) {
  return apiFetch(`/accounts/${accountId}`);
}
