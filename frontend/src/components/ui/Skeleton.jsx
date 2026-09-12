import { cn } from "../../utils/cn";
import "./Skeleton.css";

/**
 * <Skeleton width="60%" height={16} radius="sm|md|full" />
 */
export function Skeleton({ width = "100%", height = 16, radius = "sm", className, style, ...rest }) {
  return (
    <span
      className={cn("skeleton", `skeleton--radius-${radius}`, className)}
      style={{ width, height, ...style }}
      aria-hidden="true"
      {...rest}
    />
  );
}
