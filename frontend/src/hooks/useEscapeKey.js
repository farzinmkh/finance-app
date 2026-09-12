import { useEffect } from "react";

/** Calls `handler` when the Escape key is pressed while `enabled` is true. */
export function useEscapeKey(handler, enabled = true) {
  useEffect(() => {
    if (!enabled) return undefined;

    function listener(event) {
      if (event.key === "Escape") handler(event);
    }

    document.addEventListener("keydown", listener);
    return () => document.removeEventListener("keydown", listener);
  }, [handler, enabled]);
}
