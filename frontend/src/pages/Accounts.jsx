import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Wallet, Plus } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/Button";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { AccountCard } from "./accounts/AccountCard";
import { AccountFormModal } from "./accounts/AccountFormModal";
import { AccountsSkeleton } from "./accounts/AccountsSkeleton";
import { useAccountsData } from "./accounts/useAccountsData";
import "./Accounts.css";

const INITIAL_MODAL_STATE = { open: false, mode: "create", account: null };

export default function Accounts() {
  const navigate = useNavigate();
  const { status, accounts, refetch, create, update, remove } = useAccountsData();

  const [modal, setModal] = useState(INITIAL_MODAL_STATE);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  function openCreate() {
    setModal({ open: true, mode: "create", account: null });
  }

  function openEdit(account) {
    setModal({ open: true, mode: "edit", account });
  }

  function closeModal() {
    setModal(INITIAL_MODAL_STATE);
  }

  function viewTransactions(account) {
    navigate(`/transactions?account=${account.id}`);
  }

  async function handleSubmit(mode, values, accountId) {
    if (mode === "edit") {
      return update(accountId, { name: values.name, accountType: values.accountType });
    }
    return create({
      name: values.name,
      accountType: values.accountType,
      currency: values.currency,
      openingBalance: values.openingBalance || "0",
    });
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setDeleting(true);
    const success = await remove(pendingDelete.id);
    setDeleting(false);
    if (success) setPendingDelete(null);
  }

  return (
    <PageContainer>
      <div className="accounts-page__header">
        <h1 className="text-page-title">Accounts</h1>
        <Button onClick={openCreate}>
          <Plus size={16} aria-hidden="true" />
          Add Account
        </Button>
      </div>

      {status === "loading" && <AccountsSkeleton />}

      {status === "error" && (
        <ErrorState
          title="Couldn't load accounts"
          description="Check your connection and try again."
          action={<Button onClick={refetch}>Retry</Button>}
        />
      )}

      {status === "empty" && (
        <EmptyState
          icon={<Wallet size={22} />}
          title="No accounts yet."
          description="Add your first account to start tracking balances and transactions."
          action={<Button onClick={openCreate}>Add Account</Button>}
        />
      )}

      {status === "success" && (
        <div className="accounts-grid">
          {accounts.map((account) => (
            <AccountCard
              key={account.id}
              account={account}
              onEdit={openEdit}
              onDelete={setPendingDelete}
              onViewTransactions={viewTransactions}
            />
          ))}
        </div>
      )}

      {modal.open && (
        <AccountFormModal
          open={modal.open}
          mode={modal.mode}
          account={modal.account}
          onClose={closeModal}
          onSubmit={handleSubmit}
        />
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete account?"
        description={`This action cannot be undone. "${pendingDelete?.name}" will be permanently removed.`}
        confirmLabel="Delete"
        tone="danger"
        loading={deleting}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
    </PageContainer>
  );
}
