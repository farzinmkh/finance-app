import { useId, useState } from "react";
import { cn } from "../../utils/cn";
import "./Tabs.css";

/**
 * <Tabs items={[{ value: "overview", label: "Overview", content: <... /> }]} defaultValue="overview" />
 * Uncontrolled by default; pass `value` + `onChange` to control externally.
 */
export function Tabs({ items, defaultValue, value, onChange, className }) {
  const baseId = useId();
  const [internalValue, setInternalValue] = useState(defaultValue ?? items[0]?.value);
  const activeValue = value ?? internalValue;

  function selectTab(nextValue) {
    setInternalValue(nextValue);
    onChange?.(nextValue);
  }

  function handleKeyDown(event, index) {
    if (!["ArrowRight", "ArrowLeft"].includes(event.key)) return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    const nextIndex = (index + direction + items.length) % items.length;
    selectTab(items[nextIndex].value);
    document.getElementById(`${baseId}-tab-${items[nextIndex].value}`)?.focus();
  }

  const activeItem = items.find((item) => item.value === activeValue);

  return (
    <div className={cn("tabs", className)}>
      <div className="tabs__list" role="tablist">
        {items.map((item, index) => {
          const selected = item.value === activeValue;
          return (
            <button
              key={item.value}
              id={`${baseId}-tab-${item.value}`}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={`${baseId}-panel-${item.value}`}
              tabIndex={selected ? 0 : -1}
              className={cn("tabs__tab", selected && "tabs__tab--active")}
              onClick={() => selectTab(item.value)}
              onKeyDown={(e) => handleKeyDown(e, index)}
            >
              {item.label}
            </button>
          );
        })}
      </div>
      {activeItem && (
        <div
          id={`${baseId}-panel-${activeItem.value}`}
          role="tabpanel"
          aria-labelledby={`${baseId}-tab-${activeItem.value}`}
          className="tabs__panel"
        >
          {activeItem.content}
        </div>
      )}
    </div>
  );
}
