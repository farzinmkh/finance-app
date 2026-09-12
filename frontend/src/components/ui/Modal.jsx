import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { useEscapeKey } from "../../hooks/useEscapeKey";
import { cn } from "../../utils/cn";
import "./Overlay.css";

/**
 * <Modal open={open} onClose={() => setOpen(false)} title="Delete account">
 *   ...body...
 *   <Modal.Footer><Button ...>Cancel</Button><Button variant="danger">Delete</Button></Modal.Footer>
 * </Modal>
 *
 * `panelClassName` is an optional escape hatch for a specific instance to
 * override panel styling (e.g. going near-full-screen on mobile) without
 * affecting every other Modal in the app.
 */
export function Modal({ open, onClose, title, description, size = "md", panelClassName, children }) {
  const panelRef = useRef(null);

  useEscapeKey(onClose, open);

  useEffect(() => {
    if (!open) return undefined;
    const previouslyFocused = document.activeElement;
    panelRef.current?.focus();
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
      if (previouslyFocused instanceof HTMLElement) previouslyFocused.focus();
    };
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div
        ref={panelRef}
        className={cn("overlay__panel", "overlay__panel--modal", `overlay__panel--${size}`, panelClassName)}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "modal-title" : undefined}
        aria-describedby={description ? "modal-description" : undefined}
        tabIndex={-1}
      >
        <div className="overlay__header">
          <div>
            {title && (
              <h2 id="modal-title" className="text-section-title">
                {title}
              </h2>
            )}
            {description && (
              <p id="modal-description" className="text-secondary overlay__description">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            className="overlay__close"
            aria-label="Close dialog"
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

Modal.Footer = function ModalFooter({ children }) {
  return <div className="overlay__footer">{children}</div>;
};
