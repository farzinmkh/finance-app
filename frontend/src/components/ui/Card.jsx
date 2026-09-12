import { cn } from "../../utils/cn";
import "./Card.css";

/**
 * <Card padding="md|lg|none" interactive>
 *   <Card.Header title="..." action={<Button .../>} />
 *   <Card.Body>...</Card.Body>
 *   <Card.Footer>...</Card.Footer>
 * </Card>
 */
export function Card({ padding = "md", interactive = false, className, children, ...rest }) {
  return (
    <div
      className={cn(
        "card",
        `card--padding-${padding}`,
        interactive && "card--interactive",
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ title, subtitle, action, className, children }) {
  return (
    <div className={cn("card__header", className)}>
      <div className="card__header-text">
        {title && <h3 className="card__title text-card-title">{title}</h3>}
        {subtitle && <p className="card__subtitle text-secondary">{subtitle}</p>}
        {children}
      </div>
      {action && <div className="card__header-action">{action}</div>}
    </div>
  );
};

Card.Body = function CardBody({ className, children }) {
  return <div className={cn("card__body", className)}>{children}</div>;
};

Card.Footer = function CardFooter({ className, children }) {
  return <div className={cn("card__footer", className)}>{children}</div>;
};
