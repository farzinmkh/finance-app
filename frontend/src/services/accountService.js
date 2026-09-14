import { apiFetch } from "./apiClient";

/**
 * Confirmed contract — accounts.py (schema, full source available) + PHASE
 * 1/2 build notes confirm the router is mounted at /api/v1/accounts.
 *   CreateAccountRequest: { name, account_type, currency, opening_balance? }
 *   UpdateAccountRequest: { name?, account_type? }  — currency and
 *     opening_balance are NOT updatable (update_account.py is explicit
 *     about why: changing currency would require re-expressing historical
 *     transactions, and opening_balance is part of the balance invariant).
 *   AccountResponse: { id, name, account_type, currency, opening_balance,
 *     current_balance, created_at } (balances are Decimal-as-string).
 *   AccountType: "checking" | "savings" | "credit" | "cash" — these are the
 *     only four values the domain enum defines; no others exist.
 */

export function listAccounts() {
  return apiFetch("/accounts");
}

export function getAccount(accountId) {
  return apiFetch(`/accounts/${accountId}`);
}

export function createAccount({ name, accountType, currency, openingBalance }) {
  return apiFetch("/accounts", {
    method: "POST",
    body: {
      name,
      account_type: accountType,
      currency,
      opening_balance: openingBalance,
    },
  });
}

export function updateAccount(accountId, { name, accountType } = {}) {
  const body = {};
  if (name !== undefined) body.name = name;
  if (accountType !== undefined) body.account_type = accountType;
  return apiFetch(`/accounts/${accountId}`, { method: "PATCH", body });
}

/**
 * UNCONFIRMED — read before using.
 * ============================================================================
 * There is no delete() in domain/repositories/account_repository.py, no
 * implementation of one in the SQLAlchemy repository, and no delete_account
 * use case anywhere in this codebase — unlike categories, budgets,
 * transactions, and transfers, all of which have a delete use case and
 * repository method. That absence is a much stronger signal than a
 * "router not mounted yet" situation: the capability doesn't exist at the
 * domain layer at all yet.
 *
 * This function calls the REST-conventional path anyway (matching every
 * other resource in this API), but it should be expected to fail (404/405)
 * until a delete_account.py use case, a repository method, and a router
 * handler are actually added on the backend. The existing ApiError/toast
 * handling will surface that honestly rather than pretending it worked.
 * ============================================================================
 */
export function deleteAccount(accountId) {
  return apiFetch(`/accounts/${accountId}`, { method: "DELETE" });
}
