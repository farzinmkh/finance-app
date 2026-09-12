import {
  LayoutDashboard,
  ArrowLeftRight,
  Wallet,
  BarChart3,
  Settings,
  User,
} from "lucide-react";

/**
 * Single source of truth for the app's primary navigation.
 * Sidebar, Topbar (page title lookup), and MobileBottomNav all read from
 * this list so routes, labels, and icons never drift out of sync.
 */
export const NAV_ITEMS = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard, mobile: true, mobileLabel: "Home" },
  { path: "/transactions", label: "Transactions", icon: ArrowLeftRight, mobile: true },
  { path: "/accounts", label: "Accounts", icon: Wallet, mobile: true },
  { path: "/analytics", label: "Analytics", icon: BarChart3, mobile: true },
];

/** Items below the divider in the sidebar. Reachable on mobile via "More". */
export const SECONDARY_NAV_ITEMS = [
  { path: "/settings", label: "Settings", icon: Settings },
  { path: "/profile", label: "Profile", icon: User },
];

export const ALL_NAV_ITEMS = [...NAV_ITEMS, ...SECONDARY_NAV_ITEMS];

/** Looks up a human-readable title for the Topbar based on the current path. */
export function getPageTitle(pathname) {
  const match = ALL_NAV_ITEMS.find((item) => pathname.startsWith(item.path));
  return match?.label ?? "";
}
