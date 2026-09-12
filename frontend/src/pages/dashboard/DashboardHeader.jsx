import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import "./DashboardHeader.css";

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

/**
 * "+ Add Transaction" navigates to /transactions with a query flag rather
 * than opening a creation flow directly — the Transactions phase hasn't
 * been built yet, so this only prepares where that flow will live without
 * inventing any backend behavior. The Transactions page can read
 * `?action=create` on mount and open its creation form/modal automatically.
 */
export function DashboardHeader() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const firstName = user?.email ? user.email.split("@")[0] : null;

  return (
    <div className="dashboard-header">
      <div className="dashboard-header__text">
        <h1 className="text-page-title">
          {getGreeting()}
          {firstName ? `, ${firstName}` : ""}
        </h1>
        <p className="text-secondary">Here's your financial overview</p>
      </div>
      <Button onClick={() => navigate("/transactions?action=create")}>
        <Plus size={16} aria-hidden="true" />
        Add Transaction
      </Button>
    </div>
  );
}
