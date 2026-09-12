import { createPortal } from "react-dom";
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from "lucide-react";
import { useToast } from "../../hooks/useToast";
import { cn } from "../../utils/cn";
import "./Toast.css";

const ICONS = {
  default: Info,
  success: CheckCircle2,
  error: XCircle,
  warning: AlertTriangle,
};

/** Mount once near the root of the app (see App.jsx). */
export function ToastViewport() {
  const { toasts, dismissToast } = useToast();

  return createPortal(
    <div className="toast-viewport" aria-live="polite" aria-atomic="false">
      {toasts.map((toast) => {
        const Icon = ICONS[toast.variant] || ICONS.default;
        return (
          <div key={toast.id} className={cn("toast", `toast--${toast.variant}`)} role="status">
            <Icon className="toast__icon" size={18} aria-hidden="true" />
            <div className="toast__content">
              {toast.title && <p className="toast__title text-label">{toast.title}</p>}
              {toast.description && (
                <p className="toast__description text-caption">{toast.description}</p>
              )}
            </div>
            <button
              type="button"
              className="toast__close"
              aria-label="Dismiss notification"
              onClick={() => dismissToast(toast.id)}
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>,
    document.body
  );
}
