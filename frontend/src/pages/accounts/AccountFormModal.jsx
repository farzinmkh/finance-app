import { useState } from "react";
import { Modal } from "../../components/ui/Modal";
import { AccountForm } from "./AccountForm";
import { buildInitialAccountValues } from "../../utils/buildAccountFormValues";

const TITLES = { create: "Add account", edit: "Edit account" };

export function AccountFormModal({ open, mode = "create", account, onClose, onSubmit }) {
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  async function handleSubmit(values) {
    setSubmitting(true);
    try {
      const success = await onSubmit(mode, values, account?.id);
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
      <AccountForm
        mode={mode}
        initialValues={buildInitialAccountValues(mode === "edit" ? account : null)}
        submitting={submitting}
        onSubmit={handleSubmit}
        onCancel={onClose}
      />
    </Modal>
  );
}
