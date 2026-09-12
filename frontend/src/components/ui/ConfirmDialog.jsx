import { Modal } from "./Modal";
import { Button } from "./Button";

/**
 * <ConfirmDialog
 *   open={open}
 *   title="Delete this account?"
 *   description="This can't be undone. All transactions will remain but lose this account link."
 *   confirmLabel="Delete"
 *   tone="danger"
 *   onConfirm={...}
 *   onCancel={() => setOpen(false)}
 *   loading={isDeleting}
 * />
 */
export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  tone = "primary",
  onConfirm,
  onCancel,
  loading = false,
}) {
  return (
    <Modal open={open} onClose={onCancel} title={title} description={description} size="sm">
      <Modal.Footer>
        <Button variant="secondary" onClick={onCancel} disabled={loading}>
          {cancelLabel}
        </Button>
        <Button variant={tone === "danger" ? "danger" : "primary"} onClick={onConfirm} loading={loading}>
          {confirmLabel}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
