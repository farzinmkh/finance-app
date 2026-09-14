import { PERIODS } from "../../utils/analyticsAggregation";
import { cn } from "../../utils/cn";
import "./PeriodSelector.css";

export function PeriodSelector({ value, onChange }) {
  return (
    <div className="period-selector" role="radiogroup" aria-label="Time period">
      {PERIODS.map((period) => (
        <button
          key={period.value}
          type="button"
          role="radio"
          aria-checked={value === period.value}
          className={cn("period-selector__option", value === period.value && "period-selector__option--active")}
          onClick={() => onChange(period.value)}
        >
          {period.label}
        </button>
      ))}
    </div>
  );
}
