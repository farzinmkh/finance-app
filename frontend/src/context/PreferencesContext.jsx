import { createContext, useCallback, useMemo, useState } from "react";

export const PreferencesContext = createContext(null);

const STORAGE_KEY = "finance-app:currency";
const DEFAULT_CURRENCY = "USD";

function readStoredCurrency() {
  return window.localStorage.getItem(STORAGE_KEY) || DEFAULT_CURRENCY;
}

/**
 * There is no user-level currency field or endpoint on the backend —
 * each Account already carries its own currency, which is real API data
 * and is never touched by this. This preference only controls the default
 * currency used for pages that aggregate across accounts (Dashboard,
 * Analytics), the same way ThemeContext controls a purely client-side
 * preference with no backend counterpart.
 */
export function PreferencesProvider({ children }) {
  const [currency, setCurrencyState] = useState(readStoredCurrency);

  const setCurrency = useCallback((next) => {
    setCurrencyState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const value = useMemo(() => ({ currency, setCurrency }), [currency, setCurrency]);

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}
