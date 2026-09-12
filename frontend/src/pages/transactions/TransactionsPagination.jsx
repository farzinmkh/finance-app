import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "../../components/ui/Button";
import "./TransactionsPagination.css";

export function TransactionsPagination({ page, totalPages, total, onPageChange }) {
  if (totalPages <= 1) return null;

  return (
    <div className="transactions-pagination">
      <span className="text-caption">
        Page {page} of {totalPages} · {total} transaction{total === 1 ? "" : "s"}
      </span>
      <div className="transactions-pagination__controls">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
        >
          <ChevronLeft size={14} aria-hidden="true" />
          Previous
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
        >
          Next
          <ChevronRight size={14} aria-hidden="true" />
        </Button>
      </div>
    </div>
  );
}
