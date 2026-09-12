import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { useEscapeKey } from "../../hooks/useEscapeKey";
import { cn } from "../../utils/cn";
import "./Overlay.css";

/**
 * <Drawer open={open} onClose={...} title="Filters" side="right">...</Drawer>
 */
export function Drawer({ open, onClose, title, side = "right", children }) {
  const panelRef = useRef(null);

  useEscapeKey(onClose, open);

  useEffect(() => {
    if (!open) return undefined;
    panelRef.current?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div
        ref={panelRef}
        className={cn("overlay__panel", "overlay__panel--drawer", `overlay__panel--drawer-${side}`)}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "drawer-title" : undefined}
        tabIndex={-1}
      >
        <div className="overlay__header">
          {title && (
            <h2 id="drawer-title" className="text-section-title">
              {title}
            </h2>
          )}
          <button
            type="button"
            className="overlay__close"
            aria-label="Close panel"
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </div>
        <div className="overlay__body">{children}</div>
      </div>
    </div>,
    document.body
  );
}
