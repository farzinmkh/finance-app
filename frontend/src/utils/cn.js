/**
 * Joins class names, skipping falsy values.
 * cn("btn", isActive && "btn--active", size && `btn--${size}`)
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}
