/**
 * Mirrors domain/entities/account.py + accounts.py schema validation:
 * name required (≤100 chars), currency exactly 3 alphabetic characters,
 * opening balance must be a plain number (any sign — a credit account can
 * legitimately start negative, per CreateAccountRequest's own docstring).
 */
export function validateAccountForm(values, { isEdit = false } = {}) {
  const errors = {};

  const trimmedName = values.name?.trim() || "";
  if (!trimmedName) {
    errors.name = "Account name is required.";
  } else if (trimmedName.length > 100) {
    errors.name = "Account name must be 100 characters or fewer.";
  }

  if (!values.accountType) {
    errors.accountType = "Account type is required.";
  }

  if (!isEdit) {
    const currency = values.currency?.trim() || "";
    if (!currency) {
      errors.currency = "Currency is required.";
    } else if (currency.length !== 3 || !/^[A-Za-z]+$/.test(currency)) {
      errors.currency = "Currency must be a 3-letter code (e.g. USD, EUR).";
    }

    if (values.openingBalance !== "" && Number.isNaN(Number(values.openingBalance))) {
      errors.openingBalance = "Opening balance must be a number.";
    }
  }

  return errors;
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}
