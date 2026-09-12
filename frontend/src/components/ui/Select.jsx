import { forwardRef, useId } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "../../utils/cn";
import "./Field.css";

/**
 * <Select label="Account type" options={[{ value: "checking", label: "Checking" }]} />
 * Uses a native <select> for full accessibility and keyboard support.
 */
export const Select = forwardRef(function Select(
  { label, hint, error, id, className, options = [], placeholder, ...rest },
  ref
) {
  const autoId = useId();
  const inputId = id || autoId;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div className={cn("field", className)}>
      {label && (
        <label className="field__label text-label" htmlFor={inputId}>
          {label}
        </label>
      )}
      <div className={cn("field__control", error && "field__control--error")}>
        <div className="field__select-wrapper">
          <select
            ref={ref}
            id={inputId}
            className="field__select"
            defaultValue={placeholder ? "" : undefined}
            aria-invalid={Boolean(error) || undefined}
            aria-describedby={cn(hintId, errorId) || undefined}
            {...rest}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown className="field__select-icon" size={16} aria-hidden="true" />
        </div>
      </div>
      {hint && !error && (
        <p id={hintId} className="field__hint text-caption">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="field__error text-caption" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});
