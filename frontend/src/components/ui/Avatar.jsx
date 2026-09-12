import { cn } from "../../utils/cn";
import "./Avatar.css";

function getInitials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  const initials = parts.slice(0, 2).map((part) => part[0]?.toUpperCase());
  return initials.join("") || "?";
}

/**
 * <Avatar name="Farzin K." src="/photo.jpg" size="sm|md|lg" />
 * Falls back to initials on a colored circle when no `src` is provided.
 */
export function Avatar({ name, src, size = "md", className, ...rest }) {
  return (
    <span
      className={cn("avatar", `avatar--${size}`, className)}
      role="img"
      aria-label={name || "User avatar"}
      {...rest}
    >
      {src ? (
        <img className="avatar__image" src={src} alt="" />
      ) : (
        <span className="avatar__initials" aria-hidden="true">
          {getInitials(name)}
        </span>
      )}
    </span>
  );
}
