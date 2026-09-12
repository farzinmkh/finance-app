import { Wallet } from "lucide-react";
import { ThemeToggle } from "../../components/ThemeToggle";
import "./AuthLayout.css";

export function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="auth-layout">
      <div className="auth-layout__topbar">
        <span className="auth-layout__brand">
          <span className="auth-layout__mark">
            <Wallet size={18} aria-hidden="true" />
          </span>
          <span className="text-card-title">Finance App</span>
        </span>
        <ThemeToggle />
      </div>
      <div className="auth-layout__center">
        <div className="auth-layout__card">
          <div className="auth-layout__heading">
            <h1 className="text-page-title">{title}</h1>
            {subtitle && <p className="text-secondary">{subtitle}</p>}
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
