import { forwardRef, useId } from "react";
import { cn } from "../../utils/cn";
import "./Field.css";

export const Textarea = forwardRef(function Textarea(
  { label, hint, error, id, className, rows = 4, ...rest },
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
        <textarea
          ref={ref}
          id={inputId}
          rows={rows}
          className="field__textarea"
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={cn(hintId, errorId) || undefined}
          {...rest}
        />
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
