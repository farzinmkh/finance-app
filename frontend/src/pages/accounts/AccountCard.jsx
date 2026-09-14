import { MoreHorizontal, Pencil, Trash2, ArrowRightLeft } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Dropdown } from "../../components/ui/Dropdown";
import { Button } from "../../components/ui/Button";
import { getAccountTypeConfig } from "./accountTypeConfig";
import { formatCurrency } from "../../utils/format";
import { cn } from "../../utils/cn";
import "./AccountCard.css";

export function AccountCard({ account, onEdit, onDelete, onViewTransactions }) {
  const typeConfig = getAccountTypeConfig(account.account_type);
  const Icon = typeConfig.icon;
  const isNegative = Number(account.current_balance) < 0;

  return (
    <Card className="account-card">
      <div className="account-card__top">
        <span className="account-card__icon">
          <Icon size={18} aria-hidden="true" />
        </span>
        <Dropdown
          align="end"
          trigger={
            <Button variant="ghost" size="sm" iconOnly aria-label="Account actions">
              <MoreHorizontal size={16} />
            </Button>
          }
        >
          <Dropdown.Item onClick={() => onViewTransactions(account)}>
            <ArrowRightLeft size={14} /> View Transactions
          </Dropdown.Item>
          <Dropdown.Item onClick={() => onEdit(account)}>
            <Pencil size={14} /> Edit
          </Dropdown.Item>
          <Dropdown.Separator />
          <Dropdown.Item tone="danger" onClick={() => onDelete(account)}>
            <Trash2 size={14} /> Delete
          </Dropdown.Item>
        </Dropdown>
      </div>

      <p className="account-card__name text-card-title">{account.name}</p>
      <Badge tone="neutral" className="account-card__type-badge">
        {typeConfig.label}
      </Badge>

      <p className={cn("account-card__balance text-mono", isNegative && "account-card__balance--negative")}>
        {formatCurrency(account.current_balance, { currency: account.currency })}
      </p>

      <div className="account-card__footer">
        <span className="text-caption">{account.currency}</span>
        <span className="text-caption">
          {account.transactionCount === null
            ? "— transactions"
            : `${account.transactionCount} transaction${account.transactionCount === 1 ? "" : "s"}`}
        </span>
      </div>
    </Card>
  );
}
