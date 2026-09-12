import { ArrowDownLeft, ArrowUpRight } from "lucide-react";
import { Badge } from "../../components/ui/Badge";
import { formatCurrency, formatDate } from "../../utils/format";
import { cn } from "../../utils/cn";
import { TransactionRowActions } from "./TransactionRowActions";
import "./TransactionsTable.css";

/**
 * Visible from tablet width up (see TransactionsTable.css); replaced by
 * TransactionsCardList below 640px so nobody has to scroll a wide table
 * sideways on a phone. The Account column hides at tablet widths to keep
 * the row from feeling cramped — desktop shows every column.
 */
export function TransactionsTable({ items, categoriesById, accountsById, onEdit, onDuplicate, onDelete }) {
  return (
    <div className="transactions-table-wrapper">
      <table className="transactions-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th className="transactions-table__account-col">Account</th>
            <th className="transactions-table__amount-col">Amount</th>
            <th className="transactions-table__actions-col">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((tx) => {
            const isIncome = tx.transaction_type === "income";
            const category = categoriesById.get(tx.category_id);
            const account = accountsById.get(tx.account_id);
            return (
              <tr key={tx.id}>
                <td className="text-secondary">{formatDate(tx.date)}</td>
                <td>
                  <div className="transactions-table__description">
                    <span
                      className={cn(
                        "transactions-table__type-icon",
                        isIncome
                          ? "transactions-table__type-icon--income"
                          : "transactions-table__type-icon--expense"
                      )}
                      aria-hidden="true"
                    >
                      {isIncome ? <ArrowDownLeft size={14} /> : <ArrowUpRight size={14} />}
                    </span>
                    <span className="text-body">{tx.notes || "—"}</span>
                    {tx.transfer_id && (
                      <Badge tone="primary" className="transactions-table__transfer-badge">
                        Transfer
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="text-secondary">{category?.name || "Uncategorized"}</td>
                <td className="text-secondary transactions-table__account-col">
                  {account?.name || "—"}
                </td>
                <td
                  className={cn(
                    "text-mono text-label transactions-table__amount-col",
                    isIncome ? "transactions-table__amount--income" : "transactions-table__amount--expense"
                  )}
                >
                  {isIncome ? "+" : "−"}
                  {formatCurrency(tx.amount, { signDisplay: "never" })}
                </td>
                <td className="transactions-table__actions-col">
                  <TransactionRowActions
                    transaction={tx}
                    onEdit={onEdit}
                    onDuplicate={onDuplicate}
                    onDelete={onDelete}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
