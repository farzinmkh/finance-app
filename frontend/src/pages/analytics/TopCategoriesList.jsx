import { ListOrdered } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import { EmptyState } from "../../components/ui/EmptyState";
import { formatCurrency, formatPercent } from "../../utils/format";
import "./TopCategoriesList.css";

const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
];

/** `categories`: [{ category_name, amount, percentage }, ...]. */
export function TopCategoriesList({ categories, loading, empty }) {
  return (
    <Card className="top-categories-list" padding="none">
      <div className="top-categories-list__header">
        <Card.Header title="Top Categories" subtitle="Category, amount, and share of total spending" />
      </div>

      {loading ? (
        <div className="top-categories-list__skeleton">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} height={20} />
          ))}
        </div>
      ) : empty || !categories?.length ? (
        <div className="top-categories-list__empty">
          <EmptyState icon={<ListOrdered size={22} />} title="No categorized expenses yet" />
        </div>
      ) : (
        <table className="top-categories-list__table">
          <thead>
            <tr>
              <th>Category</th>
              <th className="top-categories-list__amount-col">Amount</th>
              <th className="top-categories-list__percent-col">% of spending</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((c, i) => (
              <tr key={c.category_id}>
                <td>
                  <span
                    className="top-categories-list__swatch"
                    style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
                  />
                  {c.category_name}
                </td>
                <td className="text-mono top-categories-list__amount-col">{formatCurrency(c.amount)}</td>
                <td className="text-mono top-categories-list__percent-col">{formatPercent(c.percentage)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}
