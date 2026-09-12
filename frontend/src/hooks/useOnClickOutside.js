import { useEffect } from "react";

/**
 * Calls `handler` when a pointer event occurs outside the referenced element.
 * Used by Dropdown and Modal to close on outside click.
 */
export function useOnClickOutside(ref, handler, enabled = true) {
  useEffect(() => {
    if (!enabled) return undefined;

    function listener(event) {
      const el = ref.current;
      if (!el || el.contains(event.target)) return;
      handler(event);
    }

    document.addEventListener("mousedown", listener);
    document.addEventListener("touchstart", listener);
    return () => {
      document.removeEventListener("mousedown", listener);
      document.removeEventListener("touchstart", listener);
    };
  }, [ref, handler, enabled]);
}
