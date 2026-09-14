import { forwardRef, useId } from "react";
import { Check } from "lucide-react";
import { cn } from "../../utils/cn";
import "./Checkbox.css";

/**
 * <Checkbox label="Remember me" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
 * A real native <input type="checkbox"> under the hood (keyboard support,
 * screen readers, forms all work for free) — the checkmark icon is purely
 * decorative and hidden from assistive tech.
 */
export const Checkbox = forwardRef(function Checkbox({ label, id, className, ...rest }, ref) {
  const autoId = useId();
  const inputId = id || autoId;

  return (
    <label className={cn("checkbox", className)} htmlFor={inputId}>
      <span className="checkbox__box">
        <input ref={ref} id={inputId} type="checkbox" className="checkbox__input" {...rest} />
        <Check size={12} strokeWidth={3} className="checkbox__mark" aria-hidden="true" />
      </span>
      {label && <span className="checkbox__label text-body">{label}</span>}
    </label>
  );
});
