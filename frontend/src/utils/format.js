/**
 * The backend serialises money as decimal strings (see accounts.py /
 * transfers.py schemas: "1234.5600" not 1234.56) to avoid float precision
 * loss in transit. These helpers parse that string only for *display* —
 * never for arithmetic, which must stay on the backend or use a decimal
 * library if ever needed client-side.
 */

export function formatCurrency(value, { currency = "USD", signDisplay = "auto" } = {}) {
  const amount = typeof value === "string" ? Number(value) : value;
  if (amount === null || amount === undefined || Number.isNaN(amount)) return "—";

  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    signDisplay,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercent(value, { signDisplay = "auto" } = {}) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat(undefined, {
    style: "percent",
    signDisplay,
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(value / 100);
}

export function formatDate(value, options = { month: "short", day: "numeric" }) {
  if (!value) return "—";
  const date = typeof value === "string" ? new Date(value) : value;
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat(undefined, options).format(date);
}
