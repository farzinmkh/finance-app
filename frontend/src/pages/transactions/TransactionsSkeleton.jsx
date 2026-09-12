import { Skeleton } from "../../components/ui/Skeleton";
import "./TransactionsSkeleton.css";

export function TransactionsSkeleton({ rows = 8 }) {
  return (
    <div className="transactions-skeleton" aria-hidden="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="transactions-skeleton__row">
          <Skeleton width={36} height={36} radius="full" />
          <div className="transactions-skeleton__text">
            <Skeleton width="40%" height={14} />
            <Skeleton width="25%" height={12} style={{ marginTop: 6 }} />
          </div>
          <Skeleton width={70} height={16} />
        </div>
      ))}
    </div>
  );
}
