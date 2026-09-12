import { NavLink } from "react-router-dom";
import { Wallet } from "lucide-react";
import { NAV_ITEMS, SECONDARY_NAV_ITEMS } from "../../config/navigation";
import { Avatar } from "../ui/Avatar";
import { useAuth } from "../../hooks/useAuth";
import { cn } from "../../utils/cn";
import "./Sidebar.css";

/**
 * Fixed sidebar for desktop and tablet. Collapses to icon-only at tablet
 * widths (see Sidebar.css) so it never competes for space with content;
 * on mobile it is not rendered at all — MobileBottomNav takes over.
 */
export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__mark">
          <Wallet size={18} aria-hidden="true" />
        </span>
        <span className="sidebar__brand-name text-card-title">Finance App</span>
      </div>

      <nav className="sidebar__nav" aria-label="Primary">
        <ul className="sidebar__list">
          {NAV_ITEMS.map((item) => (
            <SidebarLink key={item.path} item={item} />
          ))}
        </ul>

        <div className="sidebar__divider" role="separator" />

        <ul className="sidebar__list">
          {SECONDARY_NAV_ITEMS.map((item) => (
            <SidebarLink key={item.path} item={item} />
          ))}
        </ul>
      </nav>

      <div className="sidebar__footer">
        <Avatar name={user?.email} size="sm" />
        <div className="sidebar__footer-text">
          <p className="sidebar__footer-name text-label">{user?.email || "Guest"}</p>
          <p className="sidebar__footer-workspace text-caption">Personal</p>
        </div>
      </div>
    </aside>
  );
}

function SidebarLink({ item }) {
  const Icon = item.icon;
  return (
    <li>
      <NavLink
        to={item.path}
        className={({ isActive }) => cn("sidebar__link", isActive && "sidebar__link--active")}
      >
        <Icon size={18} aria-hidden="true" className="sidebar__link-icon" />
        <span className="sidebar__link-label">{item.label}</span>
      </NavLink>
    </li>
  );
}
