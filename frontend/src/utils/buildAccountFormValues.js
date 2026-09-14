export function buildInitialAccountValues(account) {
  if (!account) {
    return { name: "", accountType: "checking", currency: "USD", openingBalance: "0" };
  }
  return {
    name: account.name,
    accountType: account.account_type,
    currency: account.currency,
    openingBalance: String(account.opening_balance),
  };
}
