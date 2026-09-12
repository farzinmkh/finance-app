function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Builds the form's initial field values from a transaction row (edit) or a
 * duplication source. Never carries the original id forward — duplicating
 * is creating a new transaction that happens to start with the same fields.
 */
export function buildInitialValues(transaction) {
  if (!transaction) {
    return {
      type: "expense",
      amount: "",
      accountId: "",
      categoryId: "",
      fromAccountId: "",
      toAccountId: "",
      date: todayIso(),
      notes: "",
    };
  }
  return {
    type: transaction.transaction_type,
    amount: transaction.amount != null ? String(transaction.amount) : "",
    accountId: transaction.account_id || "",
    categoryId: transaction.category_id || "",
    fromAccountId: "",
    toAccountId: "",
    date: transaction.date || todayIso(),
    notes: transaction.notes || "",
  };
}
