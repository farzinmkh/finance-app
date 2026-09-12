/**
 * Mirrors validation already enforced server-side (domain/entities/transaction.py,
 * domain/entities/transfer.py) so the person sees the same rule instantly
 * instead of round-tripping to the API first. The backend remains the
 * source of truth — this is a UX layer, not a replacement for it.
 */
export function validateTransactionForm(values) {
  const errors = {};

  const amountNumber = Number(values.amount);
  if (values.amount === "" || values.amount === null || values.amount === undefined) {
    errors.amount = "Amount is required.";
  } else if (Number.isNaN(amountNumber) || amountNumber <= 0) {
    errors.amount = "Amount must be a number greater than zero.";
  } else if (!/^\d+(\.\d{1,4})?$/.test(String(values.amount).trim())) {
    errors.amount = "Amount can have at most 4 decimal places.";
  }

  if (!values.date) {
    errors.date = "Date is required.";
  }

  if (values.notes && values.notes.length > 500) {
    errors.notes = "Notes must be 500 characters or fewer.";
  }

  if (values.type === "transfer") {
    if (!values.fromAccountId) {
      errors.fromAccountId = "Source account is required.";
    }
    if (!values.toAccountId) {
      errors.toAccountId = "Destination account is required.";
    }
    if (
      values.fromAccountId &&
      values.toAccountId &&
      values.fromAccountId === values.toAccountId
    ) {
      errors.toAccountId = "Source and destination accounts must be different.";
    }
  } else if (!values.accountId) {
    errors.accountId = "Account is required.";
  }

  return errors;
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}
