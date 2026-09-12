import { apiFetch } from "./apiClient";

/**
 * Confirmed contract — see TRANSACTIONS_ROUTER_SUMMARY.md:
 *
 *   POST   /transactions          create; body: { account_id, transaction_type,
 *                                  amount, date, category_id?, notes? }
 *   GET    /transactions          paginated (page, page_size) + filterable
 *                                  (account_id, transaction_type, category_id,
 *                                  date_from, date_to) -> { items, total, page,
 *                                  page_size, total_pages }. Fixed server-side
 *                                  order: date desc, then created_at desc.
 *                                  NOTE: there is no confirmed `search` or
 *                                  `sort` query param — the UI implements
 *                                  those client-side over the loaded page
 *                                  (see pages/transactions/useTransactionsData.js).
 *   GET    /transactions/{id}     get one
 *   PUT    /transactions/{id}     partial update; body: { amount?, transaction_type?,
 *                                  date?, notes?, category_id?, clear_category? }.
 *                                  account_id is NOT updatable (delete + recreate
 *                                  instead — enforced by the backend).
 *   DELETE /transactions/{id}     delete; reverses the account balance effect.
 *
 * TransactionResponse mirrors the Transaction domain entity:
 *   { id, account_id, category_id, transaction_type, amount, date, notes,
 *     transfer_id, created_at }
 * `transfer_id` non-null means this row is one leg of a transfer — the
 * backend rejects independent edit/delete on those (TransactionLockedError,
 * HTTP 422) and the UI disables those actions accordingly.
 */

export function listTransactions({
  page = 1,
  pageSize = 50,
  accountId,
  transactionType,
  categoryId,
  dateFrom,
  dateTo,
} = {}) {
  const params = new URLSearchParams();
  params.set("page", page);
  params.set("page_size", pageSize);
  if (accountId) params.set("account_id", accountId);
  if (transactionType) params.set("transaction_type", transactionType);
  if (categoryId) params.set("category_id", categoryId);
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  return apiFetch(`/transactions?${params.toString()}`);
}

export function getTransaction(id) {
  return apiFetch(`/transactions/${id}`);
}

export function createTransaction({ accountId, transactionType, amount, date, categoryId, notes }) {
  return apiFetch("/transactions", {
    method: "POST",
    body: {
      account_id: accountId,
      transaction_type: transactionType,
      amount,
      date,
      category_id: categoryId || null,
      notes: notes || null,
    },
  });
}

/**
 * `clearCategory: true` removes the category; passing `categoryId` changes
 * it; omitting both leaves the existing category untouched (see the
 * contract note above — this three-way distinction is why `clearCategory`
 * exists as its own flag rather than relying on `categoryId` being null).
 */
export function updateTransaction(id, { amount, transactionType, date, notes, categoryId, clearCategory } = {}) {
  const body = {};
  if (amount !== undefined) body.amount = amount;
  if (transactionType !== undefined) body.transaction_type = transactionType;
  if (date !== undefined) body.date = date;
  if (notes !== undefined) body.notes = notes;
  if (clearCategory) {
    body.clear_category = true;
  } else if (categoryId !== undefined) {
    body.category_id = categoryId;
  }
  return apiFetch(`/transactions/${id}`, { method: "PUT", body });
}

export function deleteTransaction(id) {
  return apiFetch(`/transactions/${id}`, { method: "DELETE" });
}
