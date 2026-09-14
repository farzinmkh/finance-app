import { useCallback, useEffect, useState } from "react";
import * as accountService from "../../services/accountService";
import { listTransactions } from "../../services/transactionService";
import { useToast } from "../../hooks/useToast";
import { ApiError } from "../../services/apiClient";

function errorMessage(err, fallback) {
  return err instanceof ApiError ? err.message || fallback : fallback;
}

/**
 * AccountResponse has no transaction-count field, and there's no dedicated
 * count endpoint — but /transactions?account_id=X&page_size=1 legitimately
 * returns `total` for that account under the confirmed contract, so the
 * count is derived from that rather than invented. This is one extra
 * request per account (N+1), which is the same tradeoff already accepted
 * elsewhere in this codebase (see list_budgets.py's own comment: "This is
 * N queries for N budgets... for personal finance... this is fine").
 */
async function withTransactionCounts(accounts) {
  const counts = await Promise.all(
    accounts.map((account) =>
      listTransactions({ accountId: account.id, page: 1, pageSize: 1 })
        .then((result) => result.total)
        .catch(() => null) // count is a nice-to-have; don't fail the whole page over it
    )
  );
  return accounts.map((account, i) => ({ ...account, transactionCount: counts[i] }));
}

export function useAccountsData() {
  const [state, setState] = useState({ status: "loading", accounts: [], error: null });
  const { addToast } = useToast();

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, status: "loading", error: null }));
    try {
      const accounts = await accountService.listAccounts();
      const enriched = await withTransactionCounts(accounts);
      setState({ status: enriched.length === 0 ? "empty" : "success", accounts: enriched, error: null });
    } catch (error) {
      setState({ status: "error", accounts: [], error });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = useCallback(
    async (input) => {
      try {
        await accountService.createAccount(input);
        addToast({ variant: "success", title: "Account created" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't create account",
          description: errorMessage(error, "Please check the form and try again."),
        });
        return false;
      }
    },
    [addToast, load]
  );

  const update = useCallback(
    async (id, input) => {
      try {
        await accountService.updateAccount(id, input);
        addToast({ variant: "success", title: "Account updated" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't update account",
          description: errorMessage(error, "Please check the form and try again."),
        });
        return false;
      }
    },
    [addToast, load]
  );

  const remove = useCallback(
    async (id) => {
      try {
        await accountService.deleteAccount(id);
        addToast({ variant: "success", title: "Account deleted" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't delete account",
          description: errorMessage(
            error,
            "Deleting accounts may not be supported by the backend yet."
          ),
        });
        return false;
      }
    },
    [addToast, load]
  );

  return { ...state, refetch: load, create, update, remove };
}
