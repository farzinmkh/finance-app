import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { MoreHorizontal, LogOut } from "lucide-react";
import { NAV_ITEMS, SECONDARY_NAV_ITEMS } from "../../config/navigation";
import { Drawer } from "../ui/Drawer";
import { useAuth } from "../../hooks/useAuth";
import { cn } from "../../utils/cn";
import "./MobileBottomNav.css";

/**
 * Replaces the sidebar on mobile. Home/Transactions/Accounts/Analytics are
 * one tap away; anything else (Settings, Profile, log out) lives behind
 * "More" so the bar never grows past five touch-friendly targets.
 */
export function MobileBottomNav() {
  const [moreOpen, setMoreOpen] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <>
      <nav className="mobile-nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn("mobile-nav__item", isActive && "mobile-nav__item--active")
              }
            >
              <Icon size={20} aria-hidden="true" />
              <span className="mobile-nav__label">{item.mobileLabel || item.label}</span>
            </NavLink>
          );
        })}
        <button
          type="button"
          className="mobile-nav__item"
          aria-haspopup="dialog"
          aria-expanded={moreOpen}
          onClick={() => setMoreOpen(true)}
        >
          <MoreHorizontal size={20} aria-hidden="true" />
          <span className="mobile-nav__label">More</span>
        </button>
      </nav>

      <Drawer open={moreOpen} onClose={() => setMoreOpen(false)} title="More" side="right">
        <div className="mobile-nav__more-list">
          {SECONDARY_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className="mobile-nav__more-link"
                onClick={() => setMoreOpen(false)}
              >
                <Icon size={18} aria-hidden="true" />
                {item.label}
              </NavLink>
            );
          })}
          <button
            type="button"
            className="mobile-nav__more-link mobile-nav__more-link--danger"
            onClick={() => {
              setMoreOpen(false);
              logout();
              navigate("/login");
            }}
          >
            <LogOut size={18} aria-hidden="true" />
            Log out
          </button>
        </div>
      </Drawer>
    </>
  );
}
