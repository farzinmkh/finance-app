import { createContext, useCallback, useMemo, useState } from "react";

export const ToastContext = createContext(null);

let idCounter = 0;

/**
 * Provides `toasts` (current queue) and `addToast` / `dismissToast` to the
 * app. The <ToastViewport /> component (src/components/ui/Toast.jsx)
 * subscribes to this and renders the visible stack.
 *
 * addToast({ title, description, variant, duration })
 *   variant: "default" | "success" | "error" | "warning"
 *   duration: ms before auto-dismiss (default 4000; pass 0 to persist)
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    ({ title, description, variant = "default", duration = 4000 } = {}) => {
      const id = ++idCounter;
      setToasts((current) => [...current, { id, title, description, variant }]);
      if (duration > 0) {
        setTimeout(() => dismissToast(id), duration);
      }
      return id;
    },
    [dismissToast]
  );

  const value = useMemo(
    () => ({ toasts, addToast, dismissToast }),
    [toasts, addToast, dismissToast]
  );

  return (
    <ToastContext.Provider value={value}>{children}</ToastContext.Provider>
  );
}
