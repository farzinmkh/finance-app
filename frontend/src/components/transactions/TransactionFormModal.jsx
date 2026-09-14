import { useState } from "react";
import { Modal } from "../ui/Modal";
import { TransactionForm } from "./TransactionForm";
import { buildInitialValues } from "../../utils/buildTransactionFormValues";

const TITLES = {
  create: "Add transaction",
  edit: "Edit transaction",
  duplicate: "Duplicate transaction",
};

/**
 * `mode`: "create" | "edit" | "duplicate". "duplicate" behaves like create
 * (no id is ever sent) but pre-fills from `sourceTransaction` — see
 * buildInitialValues, which never carries the original id forward.
 *
 * `onSubmitExpenseIncome(mode, values, transactionId)` and
 * `onSubmitTransfer(values)` are provided by the page, which knows how to
 * call the right service (transactionService vs the unconfirmed
 * transferService — see services/transferService.js) and returns a
 * boolean indicating success so this component knows whether to close.
 */
export function TransactionFormModal({
  open,
  mode = "create",
  sourceTransaction,
  accounts,
  categories,
  onClose,
  onSubmitExpenseIncome,
  onSubmitTransfer,
}) {
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  async function handleSubmit(values) {
    setSubmitting(true);
    try {
      const success =
        values.type === "transfer"
          ? await onSubmitTransfer(values)
          : await onSubmitExpenseIncome(mode, values, sourceTransaction?.id);
      if (success) onClose();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={submitting ? () => {} : onClose}
      title={TITLES[mode]}
      size="md"
      panelClassName="overlay__panel--fullscreen-mobile"
    >
      <TransactionForm
        mode={mode === "edit" ? "edit" : "create"}
        initialValues={buildInitialValues(mode === "create" ? null : sourceTransaction)}
        accounts={accounts}
        categories={categories}
        accountLocked={mode === "edit"}
        submitting={submitting}
        onSubmit={handleSubmit}
        onCancel={onClose}
      />
    </Modal>
  );
}
