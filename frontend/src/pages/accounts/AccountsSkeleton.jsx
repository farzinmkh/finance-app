import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import "./AccountsSkeleton.css";

export function AccountsSkeleton({ count = 4 }) {
  return (
    <div className="accounts-skeleton" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="accounts-skeleton__card">
          <Skeleton width={36} height={36} radius="md" />
          <Skeleton width="60%" height={16} style={{ marginTop: 12 }} />
          <Skeleton width="35%" height={12} style={{ marginTop: 8 }} />
          <Skeleton width="50%" height={26} style={{ marginTop: 16 }} />
        </Card>
      ))}
    </div>
  );
}
