import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Card } from "../components/ui/Card";
import { Select } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import { NotAvailableNotice } from "../components/NotAvailableNotice";
import { ThemeOptionGrid } from "./settings/ThemeOptionGrid";
import { useAuth } from "../hooks/useAuth";
import { usePreferences } from "../hooks/usePreferences";
import { CURRENCY_OPTIONS } from "../utils/currencyOptions";
import "./Settings.css";

/**
 * Every section here is either backed by a real, already-working part of
 * this app (theme, currency display preference, logout) or is shown with
 * an honest NotAvailableNotice rather than a control that looks functional
 * but silently does nothing — the backend has no endpoints for
 * notifications, password change, or data export/import/account deletion.
 */
export default function Settings() {
  const { user, logout } = useAuth();
  const { currency, setCurrency } = usePreferences();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <PageContainer>
      <h1 className="text-page-title">Settings</h1>

      <Card>
        <Card.Header title="General" subtitle="Your account at a glance" />
        <dl className="settings-general">
          <div className="settings-general__row">
            <dt className="text-label">Signed in as</dt>
            <dd className="text-body">{user?.email || "—"}</dd>
          </div>
        </dl>
      </Card>

      <Card>
        <Card.Header title="Appearance" subtitle="Choose how Finance App looks on this device" />
        <ThemeOptionGrid />
      </Card>

      <Card>
        <Card.Header
          title="Currency"
          subtitle="Default currency for totals that combine multiple accounts (Dashboard, Analytics)"
        />
        <div className="settings-currency">
          <Select
            aria-label="Default currency"
            options={CURRENCY_OPTIONS}
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          />
          <p className="text-caption settings-currency__hint">
            Each account keeps its own currency for its own transactions — this only affects
            combined totals that don't belong to a single account.
          </p>
        </div>
      </Card>

      <Card>
        <Card.Header title="Notifications" subtitle="Email and in-app alerts" />
        <NotAvailableNotice>
          Notifications aren't available yet — the backend doesn't have any notification
          infrastructure (no email sending, no alert storage) to connect this to.
        </NotAvailableNotice>
      </Card>

      <Card>
        <Card.Header title="Security" subtitle="Password and session" />
        <div className="settings-security">
          <NotAvailableNotice>
            Changing your password isn't available yet — the backend has no password-change
            endpoint (only registration and sign-in exist today).
          </NotAvailableNotice>
          <div className="settings-security__logout">
            <Button variant="secondary" onClick={handleLogout}>
              <LogOut size={16} aria-hidden="true" />
              Log out
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <Card.Header title="Data" subtitle="Export, import, and account deletion" />
        <NotAvailableNotice>
          Exporting or importing your data, and deleting your account, aren't available yet —
          none of these have a backend endpoint to call. Nothing here will pretend to work
          until they do.
        </NotAvailableNotice>
      </Card>
    </PageContainer>
  );
}
