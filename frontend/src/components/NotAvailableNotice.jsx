import { Info } from "lucide-react";
import "./NotAvailableNotice.css";

/**
 * Used throughout Settings and Profile wherever the phase spec asked for a
 * feature the backend doesn't actually support yet (change password,
 * notifications, data export/import, account deletion, etc). Showing this
 * honestly is the whole point — a fake working control would be worse than
 * no control at all.
 */
export function NotAvailableNotice({ children }) {
  return (
    <div className="not-available-notice">
      <Info size={16} aria-hidden="true" className="not-available-notice__icon" />
      <p className="text-secondary">{children}</p>
    </div>
  );
}
