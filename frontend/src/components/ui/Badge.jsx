import { cn } from "../../utils/cn";
import "./Badge.css";

/**
 * <Badge tone="neutral|primary|income|expense|warning">Status</Badge>
 */
export function Badge({ tone = "neutral", className, children, ...rest }) {
  return (
    <span className={cn("badge", `badge--${tone}`, className)} {...rest}>
      {children}
    </span>
  );
}
