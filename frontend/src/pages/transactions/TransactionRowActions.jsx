import { MoreHorizontal, Pencil, Copy, Trash2 } from "lucide-react";
import { Dropdown } from "../../components/ui/Dropdown";
import { Button } from "../../components/ui/Button";

/**
 * Transactions with a non-null transfer_id are one leg of a transfer — the
 * backend rejects independent edit/delete on those with a 422
 * TransactionLockedError (see update_transaction.py / delete_transaction.py),
 * so those actions are disabled here rather than letting the person hit an
 * error after the fact.
 */
export function TransactionRowActions({ transaction, onEdit, onDuplicate, onDelete }) {
  const locked = Boolean(transaction.transfer_id);

  return (
    <Dropdown
      align="end"
      trigger={
        <Button variant="ghost" size="sm" iconOnly aria-label="Transaction actions">
          <MoreHorizontal size={16} />
        </Button>
      }
    >
      <Dropdown.Item
        onClick={() => onEdit(transaction)}
        disabled={locked}
        title={locked ? "Part of a transfer — edit the transfer instead" : undefined}
      >
        <Pencil size={14} /> Edit
      </Dropdown.Item>
      <Dropdown.Item onClick={() => onDuplicate(transaction)}>
        <Copy size={14} /> Duplicate
      </Dropdown.Item>
      <Dropdown.Separator />
      <Dropdown.Item
        tone="danger"
        onClick={() => onDelete(transaction)}
        disabled={locked}
        title={locked ? "Part of a transfer — delete the transfer instead" : undefined}
      >
        <Trash2 size={14} /> Delete
      </Dropdown.Item>
    </Dropdown>
  );
}
