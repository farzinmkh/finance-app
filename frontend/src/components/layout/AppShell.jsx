import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { MobileBottomNav } from "./MobileBottomNav";
import { ErrorBoundary } from "../ErrorBoundary";
import "./AppShell.css";

/**
 * The authenticated application frame:
 *
 *   AppShell
 *   ├── Sidebar        (desktop/tablet, fixed)
 *   ├── Topbar          (sticky, above content)
 *   └── MainContent     (routed page via <Outlet />)
 *   └── MobileBottomNav (mobile only)
 *
 * Mounted once by the router for every protected route — see App.jsx.
 * Each page is wrapped in its own ErrorBoundary so one broken page can't
 * take down the whole shell.
 */
export function AppShell() {
  return (
    <div className="app-shell-layout">
      <Sidebar />
      <div className="app-shell-layout__main">
        <Topbar />
        <main className="app-shell-layout__content">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <MobileBottomNav />
    </div>
  );
}
