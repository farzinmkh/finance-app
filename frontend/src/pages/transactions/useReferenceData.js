import { useCallback, useEffect, useState } from "react";
import { listAccounts } from "../../services/accountService";
import { listCategories } from "../../services/categoryService";

/**
 * Accounts and categories are needed by both the filter toolbar and the
 * transaction form, so they're loaded once here rather than per-component.
 * Exposes its own status so callers can distinguish "still loading" from
 * "loaded but empty" (e.g. no accounts yet — transactions can't be created).
 */
export function useReferenceData() {
  const [state, setState] = useState({
    status: "loading",
    accounts: [],
    categories: [],
    error: null,
  });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, status: "loading", error: null }));
    try {
      const [accounts, categories] = await Promise.all([listAccounts(), listCategories()]);
      setState({ status: "success", accounts, categories, error: null });
    } catch (error) {
      setState({ status: "error", accounts: [], categories: [], error });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, refetch: load };
}
