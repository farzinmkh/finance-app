import { useCallback, useEffect, useState } from "react";
import * as transactionService from "../../services/transactionService";
import { useToast } from "../../hooks/useToast";
import { ApiError } from "../../services/apiClient";

const DEFAULT_FILTERS = {
  transactionType: "",
  categoryId: "",
  accountId: "",
  dateFrom: "",
  dateTo: "",
};

function errorMessage(err, fallback) {
  return err instanceof ApiError ? err.message || fallback : fallback;
}

/**
 * Owns server communication for the Transactions page: paginated/filtered
 * fetch plus create/update/delete, each wired to toasts and an automatic
 * refetch on success. Search and sort are intentionally NOT here — the
 * confirmed API has no params for them, so the page applies those
 * client-side over `items` (see utils/transactionDisplay.js).
 */
export function useTransactionsData() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [state, setState] = useState({
    status: "loading",
    items: [],
    total: 0,
    totalPages: 1,
    error: null,
  });
  const { addToast } = useToast();

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, status: "loading", error: null }));
    try {
      const result = await transactionService.listTransactions({
        page,
        pageSize,
        transactionType: filters.transactionType || undefined,
        categoryId: filters.categoryId || undefined,
        accountId: filters.accountId || undefined,
        dateFrom: filters.dateFrom || undefined,
        dateTo: filters.dateTo || undefined,
      });
      setState({
        status: result.items.length === 0 ? "empty" : "success",
        items: result.items,
        total: result.total,
        totalPages: result.total_pages,
        error: null,
      });
    } catch (error) {
      setState({ status: "error", items: [], total: 0, totalPages: 1, error });
    }
  }, [page, pageSize, filters]);

  useEffect(() => {
    load();
  }, [load]);

  // Any filter change resets to page 1 — otherwise the person could land on
  // an out-of-range page for the newly filtered result set.
  const updateFilters = useCallback((patch) => {
    setFilters((prev) => ({ ...prev, ...patch }));
    setPage(1);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
    setPage(1);
  }, []);

  const create = useCallback(
    async (input) => {
      try {
        await transactionService.createTransaction(input);
        addToast({ variant: "success", title: "Transaction added" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't add transaction",
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
        await transactionService.updateTransaction(id, input);
        addToast({ variant: "success", title: "Transaction updated" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't update transaction",
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
        await transactionService.deleteTransaction(id);
        addToast({ variant: "success", title: "Transaction deleted" });
        await load();
        return true;
      } catch (error) {
        addToast({
          variant: "error",
          title: "Couldn't delete transaction",
          description: errorMessage(error, "Please try again."),
        });
        return false;
      }
    },
    [addToast, load]
  );

  return {
    ...state,
    filters,
    updateFilters,
    resetFilters,
    page,
    setPage,
    pageSize,
    refetch: load,
    create,
    update,
    remove,
  };
}
