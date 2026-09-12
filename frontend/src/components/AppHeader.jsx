import { Wallet } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import "./AppHeader.css";

export function AppHeader() {
  return (
    <header className="app-header">
      <div className="container app-header__inner">
        <div className="app-header__brand">
          <span className="app-header__mark">
            <Wallet size={18} aria-hidden="true" />
          </span>
          <span className="app-header__name text-card-title">Finance App</span>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
