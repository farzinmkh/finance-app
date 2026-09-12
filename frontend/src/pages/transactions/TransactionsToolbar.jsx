import { Search, Plus, X } from "lucide-react";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";
import "./TransactionsToolbar.css";

const SORT_OPTIONS = [
  { value: "date:desc", label: "Date (newest first)" },
  { value: "date:asc", label: "Date (oldest first)" },
  { value: "amount:desc", label: "Amount (high to low)" },
  { value: "amount:asc", label: "Amount (low to high)" },
  { value: "notes:asc", label: "Description (A–Z)" },
  { value: "notes:desc", label: "Description (Z–A)" },
];

export function TransactionsToolbar({
  search,
  onSearchChange,
  sort,
  onSortChange,
  filters,
  onFiltersChange,
  onResetFilters,
  accounts,
  categories,
  onAddTransaction,
  addDisabled = false,
}) {
  const hasActiveFilters =
    filters.transactionType || filters.categoryId || filters.accountId || filters.dateFrom || filters.dateTo;

  return (
    <div className="transactions-toolbar">
      <div className="transactions-toolbar__row">
        <Input
          className="transactions-toolbar__search"
          placeholder="Search this page's descriptions or categories"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          startAdornment={<Search size={16} />}
          aria-label="Search transactions"
        />
        <Button onClick={onAddTransaction} className="transactions-toolbar__add" disabled={addDisabled}>
          <Plus size={16} aria-hidden="true" />
          Add Transaction
        </Button>
      </div>

      <div className="transactions-toolbar__row transactions-toolbar__filters">
        <Select
          placeholder="All types"
          aria-label="Filter by type"
          options={[
            { value: "income", label: "Income" },
            { value: "expense", label: "Expense" },
          ]}
          value={filters.transactionType}
          onChange={(e) => onFiltersChange({ transactionType: e.target.value })}
        />
        <Select
          placeholder="All categories"
          aria-label="Filter by category"
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
          value={filters.categoryId}
          onChange={(e) => onFiltersChange({ categoryId: e.target.value })}
        />
        <Select
          placeholder="All accounts"
          aria-label="Filter by account"
          options={accounts.map((a) => ({ value: a.id, label: a.name }))}
          value={filters.accountId}
          onChange={(e) => onFiltersChange({ accountId: e.target.value })}
        />
        <Input
          type="date"
          aria-label="From date"
          value={filters.dateFrom}
          onChange={(e) => onFiltersChange({ dateFrom: e.target.value })}
        />
        <Input
          type="date"
          aria-label="To date"
          value={filters.dateTo}
          onChange={(e) => onFiltersChange({ dateTo: e.target.value })}
        />
        <Select
          aria-label="Sort by"
          options={SORT_OPTIONS}
          value={`${sort.field}:${sort.direction}`}
          onChange={(e) => {
            const [field, direction] = e.target.value.split(":");
            onSortChange({ field, direction });
          }}
        />
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onResetFilters}>
            <X size={14} aria-hidden="true" />
            Clear filters
          </Button>
        )}
      </div>
    </div>
  );
}
