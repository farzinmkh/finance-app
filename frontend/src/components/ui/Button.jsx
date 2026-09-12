import { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "../../utils/cn";
import "./Button.css";

/**
 * <Button variant="primary|secondary|ghost|danger" size="sm|md|lg" loading iconOnly aria-label="...">
 */
export const Button = forwardRef(function Button(
  {
    variant = "primary",
    size = "md",
    loading = false,
    iconOnly = false,
    disabled = false,
    className,
    children,
    type = "button",
    ...rest
  },
  ref
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(
        "btn",
        `btn--${variant}`,
        `btn--${size}`,
        iconOnly && "btn--icon-only",
        loading && "btn--loading",
        className
      )}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading && <Loader2 className="btn__spinner" size={16} aria-hidden="true" />}
      <span className="btn__content">{children}</span>
    </button>
  );
});
