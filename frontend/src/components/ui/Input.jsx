import { forwardRef, useId } from "react";
import { cn } from "../../utils/cn";
import "./Field.css";

/**
 * <Input label="Email" hint="We'll never share it" error="Required" ... />
 * Any other prop is forwarded to the native <input>.
 */
export const Input = forwardRef(function Input(
  {
    label,
    hint,
    error,
    id,
    className,
    startAdornment,
    endAdornment,
    ...rest
  },
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
        {startAdornment && (
          <span className="field__adornment field__adornment--start">
            {startAdornment}
          </span>
        )}
        <input
          ref={ref}
          id={inputId}
          className="field__input"
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={cn(hintId, errorId) || undefined}
          {...rest}
        />
        {endAdornment && (
          <span className="field__adornment field__adornment--end">
            {endAdornment}
          </span>
        )}
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
