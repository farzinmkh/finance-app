import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Receipt } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { TransactionFormModal } from "../components/transactions/TransactionFormModal";
import { TransactionsToolbar } from "./transactions/TransactionsToolbar";
import { TransactionsTable } from "./transactions/TransactionsTable";
import { TransactionsCardList } from "./transactions/TransactionsCardList";
import { TransactionsSkeleton } from "./transactions/TransactionsSkeleton";
import { TransactionsPagination } from "./transactions/TransactionsPagination";
import { useTransactionsData } from "./transactions/useTransactionsData";
import { useReferenceData } from "./transactions/useReferenceData";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useToast } from "../hooks/useToast";
import { ApiError } from "../services/apiClient";
import * as transferService from "../services/transferService";
import { applySearchAndSort } from "../utils/transactionDisplay";
import "./Transactions.css";

const INITIAL_MODAL_STATE = { open: false, mode: "create", transaction: null };

export default function Transactions() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { addToast } = useToast();

  const referenceData = useReferenceData();
  const {
    status,
    items,
    total,
    totalPages,
    page,
    setPage,
    filters,
    updateFilters,
    resetFilters,
    refetch,
    create,
    update,
    remove,
  } = useTransactionsData();

  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 250);
  const [sort, setSort] = useState({ field: "date", direction: "desc" });

  const [modal, setModal] = useState(() =>
    searchParams.get("action") === "create" ? { ...INITIAL_MODAL_STATE, open: true } : INITIAL_MODAL_STATE
  );
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const categoriesById = useMemo(
    () => new Map(referenceData.categories.map((c) => [c.id, c])),
    [referenceData.categories]
  );
  const accountsById = useMemo(
    () => new Map(referenceData.accounts.map((a) => [a.id, a])),
    [referenceData.accounts]
  );

  const displayedItems = useMemo(
    () => applySearchAndSort(items, { search: debouncedSearch, sort, categoriesById }),
    [items, debouncedSearch, sort, categoriesById]
  );

  function closeModal() {
    setModal(INITIAL_MODAL_STATE);
    // Drop the ?action=create flag (set by the Dashboard's "+ Add Transaction"
    // button) so refreshing or navigating back doesn't reopen the form.
    if (searchParams.has("action")) {
      searchParams.delete("action");
      setSearchParams(searchParams, { replace: true });
    }
  }

  function openCreate() {
    setModal({ open: true, mode: "create", transaction: null });
  }

  function openEdit(transaction) {
    setModal({ open: true, mode: "edit", transaction });
  }

  function openDuplicate(transaction) {
    setModal({ open: true, mode: "duplicate", transaction });
  }

  async function handleSubmitExpenseIncome(mode, values, transactionId) {
    const payload = {
      accountId: values.accountId,
      transactionType: values.type,
      amount: values.amount,
      date: values.date,
      categoryId: values.categoryId || undefined,
    };
    if (mode === "edit") {
      return update(transactionId, {
        amount: values.amount,
        transactionType: values.type,
        date: values.date,
        notes: values.notes || null,
        ...(values.categoryId ? { categoryId: values.categoryId } : { clearCategory: true }),
      });
    }
    return create({ ...payload, notes: values.notes || undefined });
  }

  // Transfers use a separate, unconfirmed-router service (see
  // services/transferService.js) rather than the transactions data hook,
  // since a transfer isn't a single transaction row to update in place.
  async function handleSubmitTransfer(values) {
    try {
      await transferService.createTransfer({
        fromAccountId: values.fromAccountId,
        toAccountId: values.toAccountId,
        amount: values.amount,
        date: values.date,
        notes: values.notes || undefined,
      });
      addToast({ variant: "success", title: "Transfer recorded" });
      await refetch();
      return true;
    } catch (error) {
      addToast({
        variant: "error",
        title: "Couldn't record transfer",
        description:
          error instanceof ApiError
            ? error.message || "The transfers endpoint may not be available yet."
            : "Couldn't reach the server.",
      });
      return false;
    }
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setDeleting(true);
    const success = await remove(pendingDelete.id);
    setDeleting(false);
    if (success) setPendingDelete(null);
  }

  const referenceReady = referenceData.status === "success";

  return (
    <PageContainer>
      <div className="transactions-page__header">
        <h1 className="text-page-title">Transactions</h1>
      </div>

      <TransactionsToolbar
        search={search}
        onSearchChange={setSearch}
        sort={sort}
        onSortChange={setSort}
        filters={filters}
        onFiltersChange={updateFilters}
        onResetFilters={resetFilters}
        accounts={referenceData.accounts}
        categories={referenceData.categories}
        onAddTransaction={openCreate}
        addDisabled={!referenceReady}
      />

      {referenceData.status === "error" && (
        <ErrorState
          title="Couldn't load accounts and categories"
          description="Filters and adding transactions need this data. Check your connection and try again."
          action={<Button onClick={referenceData.refetch}>Retry</Button>}
        />
      )}

      {status === "loading" && <TransactionsSkeleton />}

      {status === "error" && (
        <ErrorState
          title="Couldn't load transactions"
          description="Check your connection and try again."
          action={<Button onClick={refetch}>Retry</Button>}
        />
      )}

      {status === "empty" && (
        <EmptyState
          icon={<Receipt size={22} />}
          title="No transactions yet."
          description="Start tracking your finances by adding your first transaction."
          action={
            <Button onClick={openCreate} disabled={!referenceReady}>
              Add Transaction
            </Button>
          }
        />
      )}

      {status === "success" && (
        <>
          {displayedItems.length === 0 ? (
            <EmptyState
              title="No matching transactions"
              description="Try adjusting your search or filters."
              action={
                <Button variant="secondary" onClick={() => { setSearch(""); resetFilters(); }}>
                  Clear search and filters
                </Button>
              }
            />
          ) : (
            <>
              <TransactionsTable
                items={displayedItems}
                categoriesById={categoriesById}
                accountsById={accountsById}
                onEdit={openEdit}
                onDuplicate={openDuplicate}
                onDelete={setPendingDelete}
              />
              <TransactionsCardList
                items={displayedItems}
                categoriesById={categoriesById}
                accountsById={accountsById}
                onEdit={openEdit}
                onDuplicate={openDuplicate}
                onDelete={setPendingDelete}
              />
            </>
          )}
          <TransactionsPagination page={page} totalPages={totalPages} total={total} onPageChange={setPage} />
        </>
      )}

      {modal.open && referenceReady && (
        <TransactionFormModal
          open={modal.open}
          mode={modal.mode}
          sourceTransaction={modal.transaction}
          accounts={referenceData.accounts}
          categories={referenceData.categories}
          onClose={closeModal}
          onSubmitExpenseIncome={handleSubmitExpenseIncome}
          onSubmitTransfer={handleSubmitTransfer}
        />
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete transaction?"
        description="This action cannot be undone."
        confirmLabel="Delete"
        tone="danger"
        loading={deleting}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
    </PageContainer>
  );
}
