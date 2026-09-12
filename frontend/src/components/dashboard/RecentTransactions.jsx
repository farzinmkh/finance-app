import { Link } from "react-router-dom";
import { ArrowDownLeft, ArrowUpRight, Receipt } from "lucide-react";
import { Card } from "../ui/Card";
import { Skeleton } from "../ui/Skeleton";
import { EmptyState } from "../ui/EmptyState";
import { formatCurrency, formatDate } from "../../utils/format";
import { cn } from "../../utils/cn";
import "./RecentTransactions.css";

/**
 * <RecentTransactions items={[{ id, description, category_name, date, amount, transaction_type }]} loading empty />
 */
export function RecentTransactions({ items, loading = false, empty = false }) {
  return (
    <Card className="recent-transactions" padding="none">
      <div className="recent-transactions__header">
        <Card.Header title="Recent Transactions" subtitle="Your latest activity" />
      </div>

      {loading ? (
        <ul className="recent-transactions__list">
          {Array.from({ length: 5 }).map((_, i) => (
            <li key={i} className="recent-transactions__item">
              <Skeleton width={36} height={36} radius="full" />
              <div className="recent-transactions__item-text">
                <Skeleton width="55%" height={14} />
                <Skeleton width="35%" height={12} style={{ marginTop: 6 }} />
              </div>
              <Skeleton width={64} height={16} />
            </li>
          ))}
        </ul>
      ) : empty ? (
        <div className="recent-transactions__empty">
          <EmptyState
            icon={<Receipt size={22} />}
            title="No transactions yet"
            description="Once you record a transaction, it'll show up here."
          />
        </div>
      ) : (
        <ul className="recent-transactions__list">
          {items.map((tx) => {
            const isIncome = tx.transaction_type === "income";
            return (
              <li key={tx.id} className="recent-transactions__item">
                <span
                  className={cn(
                    "recent-transactions__icon",
                    isIncome ? "recent-transactions__icon--income" : "recent-transactions__icon--expense"
                  )}
                  aria-hidden="true"
                >
                  {isIncome ? <ArrowDownLeft size={16} /> : <ArrowUpRight size={16} />}
                </span>

                <div className="recent-transactions__item-text">
                  <p className="recent-transactions__description text-body">{tx.description}</p>
                  <p className="recent-transactions__meta text-caption">
                    {tx.category_name || "Uncategorized"} · {formatDate(tx.date)}
                  </p>
                </div>

                <span
                  className={cn(
                    "recent-transactions__amount text-mono text-label",
                    isIncome ? "recent-transactions__amount--income" : "recent-transactions__amount--expense"
                  )}
                >
                  {isIncome ? "+" : "−"}
                  {formatCurrency(tx.amount, { signDisplay: "never" })}
                </span>
              </li>
            );
          })}
        </ul>
      )}

      <div className="recent-transactions__footer">
        <Link to="/transactions" className="recent-transactions__view-all text-label">
          View all transactions
        </Link>
      </div>
    </Card>
  );
}
