import { Landmark, PiggyBank, CreditCard, Banknote } from "lucide-react";

/**
 * domain/entities/account.py defines exactly these 4 values on AccountType —
 * checking, savings, credit, cash. No "Investment" or "Other" exist on the
 * backend, so none are offered here.
 */
export const ACCOUNT_TYPES = [
  { value: "checking", label: "Checking", icon: Landmark },
  { value: "savings", label: "Savings", icon: PiggyBank },
  { value: "credit", label: "Credit Card", icon: CreditCard },
  { value: "cash", label: "Cash", icon: Banknote },
];

export const ACCOUNT_TYPE_OPTIONS = ACCOUNT_TYPES.map(({ value, label }) => ({ value, label }));

const ACCOUNT_TYPES_BY_VALUE = new Map(ACCOUNT_TYPES.map((t) => [t.value, t]));

export function getAccountTypeConfig(accountType) {
  return ACCOUNT_TYPES_BY_VALUE.get(accountType) || { label: accountType, icon: Landmark };
}
