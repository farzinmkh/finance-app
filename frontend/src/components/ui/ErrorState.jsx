import { AlertTriangle } from "lucide-react";
import { cn } from "../../utils/cn";
import "./StatePanel.css";

/**
 * <ErrorState title="Couldn't load transactions" description="Check your connection and try again." action={<Button onClick={retry}>Retry</Button>} />
 */
export function ErrorState({
  title = "Something went wrong",
  description,
  action,
  className,
}) {
  return (
    <div className={cn("state-panel", className)}>
      <div className="state-panel__icon state-panel__icon--danger">
        <AlertTriangle size={22} aria-hidden="true" />
      </div>
      <p className="state-panel__title text-card-title">{title}</p>
      {description && <p className="state-panel__description text-secondary">{description}</p>}
      {action && <div className="state-panel__action">{action}</div>}
    </div>
  );
}
