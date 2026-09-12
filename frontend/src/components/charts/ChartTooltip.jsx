import "./ChartTooltip.css";

/**
 * Drop-in replacement for recharts' default tooltip content, styled with
 * design tokens so it matches in both light and dark themes.
 *
 * <Tooltip content={<ChartTooltip valueFormatter={formatCurrency} />} />
 */
export function ChartTooltip({ active, payload, label, valueFormatter = (v) => v }) {
  if (!active || !payload?.length) return null;

  return (
    <div className="chart-tooltip" role="tooltip">
      {label && <p className="chart-tooltip__label text-label">{label}</p>}
      <ul className="chart-tooltip__list">
        {payload.map((entry) => (
          <li key={entry.dataKey || entry.name} className="chart-tooltip__item">
            <span className="chart-tooltip__swatch" style={{ backgroundColor: entry.color }} />
            <span className="chart-tooltip__name text-caption">{entry.name}</span>
            <span className="chart-tooltip__value text-label text-mono">
              {valueFormatter(entry.value)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
