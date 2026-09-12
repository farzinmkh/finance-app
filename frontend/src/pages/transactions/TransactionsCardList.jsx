import { ArrowDownLeft, ArrowUpRight } from "lucide-react";
import { Badge } from "../../components/ui/Badge";
import { formatCurrency, formatDate } from "../../utils/format";
import { cn } from "../../utils/cn";
import { TransactionRowActions } from "./TransactionRowActions";
import "./TransactionsCardList.css";

export function TransactionsCardList({ items, categoriesById, accountsById, onEdit, onDuplicate, onDelete }) {
  return (
    <ul className="transactions-card-list">
      {items.map((tx) => {
        const isIncome = tx.transaction_type === "income";
        const category = categoriesById.get(tx.category_id);
        const account = accountsById.get(tx.account_id);
        return (
          <li key={tx.id} className="transactions-card">
            <span
              className={cn(
                "transactions-card__icon",
                isIncome ? "transactions-card__icon--income" : "transactions-card__icon--expense"
              )}
              aria-hidden="true"
            >
              {isIncome ? <ArrowDownLeft size={16} /> : <ArrowUpRight size={16} />}
            </span>

            <div className="transactions-card__body">
              <div className="transactions-card__top">
                <p className="transactions-card__description text-body">{tx.notes || "—"}</p>
                <span
                  className={cn(
                    "transactions-card__amount text-mono text-label",
                    isIncome ? "transactions-card__amount--income" : "transactions-card__amount--expense"
                  )}
                >
                  {isIncome ? "+" : "−"}
                  {formatCurrency(tx.amount, { signDisplay: "never" })}
                </span>
              </div>
              <p className="transactions-card__meta text-caption">
                {category?.name || "Uncategorized"} · {account?.name || "—"} · {formatDate(tx.date)}
              </p>
              {tx.transfer_id && (
                <Badge tone="primary" className="transactions-card__transfer-badge">
                  Transfer
                </Badge>
              )}
            </div>

            <TransactionRowActions
              transaction={tx}
              onEdit={onEdit}
              onDuplicate={onDuplicate}
              onDelete={onDelete}
            />
          </li>
        );
      })}
    </ul>
  );
}
