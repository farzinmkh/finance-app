import { cn } from "../../utils/cn";
import "./StatePanel.css";

/**
 * <EmptyState icon={<Inbox />} title="No transactions yet" description="..." action={<Button>Add one</Button>} />
 */
export function EmptyState({ icon, title, description, action, className }) {
  return (
    <div className={cn("state-panel", className)}>
      {icon && <div className="state-panel__icon state-panel__icon--neutral">{icon}</div>}
      {title && <p className="state-panel__title text-card-title">{title}</p>}
      {description && <p className="state-panel__description text-secondary">{description}</p>}
      {action && <div className="state-panel__action">{action}</div>}
    </div>
  );
}
