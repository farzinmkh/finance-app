import { useLocation } from "react-router-dom";
import { getPageTitle } from "../../config/navigation";
import { ThemeToggle } from "../ThemeToggle";
import { UserMenu } from "./UserMenu";
import "./Topbar.css";

/**
 * Sits above the main content on every authenticated page. Page title is
 * derived from the current route via config/navigation.js so individual
 * pages don't need to manage it — a page can still override by rendering
 * its own heading inside PageContainer for anything more specific.
 */
export function Topbar() {
  const location = useLocation();
  const title = getPageTitle(location.pathname);

  return (
    <header className="topbar">
      <h1 className="topbar__title text-section-title">{title}</h1>
      <div className="topbar__actions">
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
