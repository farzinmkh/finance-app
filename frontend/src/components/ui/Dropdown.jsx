import { useRef, useState } from "react";
import { useOnClickOutside } from "../../hooks/useOnClickOutside";
import { useEscapeKey } from "../../hooks/useEscapeKey";
import { cn } from "../../utils/cn";
import "./Dropdown.css";

/**
 * <Dropdown trigger={<Button>Options</Button>} align="start|end">
 *   <Dropdown.Item onClick={...}>Edit</Dropdown.Item>
 *   <Dropdown.Item onClick={...} tone="danger">Delete</Dropdown.Item>
 * </Dropdown>
 */
export function Dropdown({ trigger, align = "start", children }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  useOnClickOutside(rootRef, () => setOpen(false), open);
  useEscapeKey(() => setOpen(false), open);

  return (
    <div className="dropdown" ref={rootRef}>
      <div onClick={() => setOpen((v) => !v)}>{trigger}</div>
      {open && (
        <div
          role="menu"
          className={cn("dropdown__menu", `dropdown__menu--${align}`)}
          onClick={() => setOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  );
}

Dropdown.Item = function DropdownItem({ tone = "default", className, children, ...rest }) {
  return (
    <button
      type="button"
      role="menuitem"
      className={cn("dropdown__item", `dropdown__item--${tone}`, className)}
      {...rest}
    >
      {children}
    </button>
  );
};

Dropdown.Separator = function DropdownSeparator() {
  return <div className="dropdown__separator" role="separator" />;
};
