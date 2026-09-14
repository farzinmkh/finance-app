import { Card } from "../components/ui/Card";
import { Avatar } from "../components/ui/Avatar";
import { NotAvailableNotice } from "../components/NotAvailableNotice";
import { PageContainer } from "../components/layout/PageContainer";
import { useAuth } from "../hooks/useAuth";
import "./Profile.css";

/**
 * The backend's AuthOutput (returned by both /auth/login and /auth/register
 * — see auth_use_cases.py) only ever contains { user_id, email }. There is
 * no "/auth/me" or "/users/me" endpoint anywhere in this codebase, so
 * that's genuinely everything the frontend can know about the signed-in
 * person right now:
 *   - No "name" field exists on the User domain entity at all.
 *   - created_at exists on the User entity, but is never returned by any
 *     endpoint the frontend can call — so it can't be honestly displayed
 *     here, even though the backend technically stores it.
 *   - "Last login" isn't tracked anywhere in the domain model.
 * Rather than fabricate any of these, they're shown with a clear notice.
 */
export default function Profile() {
  const { user } = useAuth();

  return (
    <PageContainer>
      <h1 className="text-page-title">Profile</h1>

      <Card>
        <div className="profile-header">
          <Avatar name={user?.email} size="lg" />
          <div className="profile-header__text">
            <p className="text-card-title">{user?.email || "—"}</p>
            <p className="text-secondary">Personal workspace</p>
          </div>
        </div>
      </Card>

      <Card>
        <Card.Header title="Personal information" />
        <div className="profile-section">
          <div className="profile-field">
            <span className="text-label">Name</span>
            <NotAvailableNotice>
              Not tracked by the backend — user accounts currently have only an email address,
              no name field.
            </NotAvailableNotice>
          </div>
          <div className="profile-field">
            <span className="text-label">Email</span>
            <p className="text-body">{user?.email || "—"}</p>
          </div>
          <NotAvailableNotice>
            Editing this information isn't available yet — there's no endpoint to update an
            existing account (only creating one at registration).
          </NotAvailableNotice>
        </div>
      </Card>

      <Card>
        <Card.Header title="Security" />
        <NotAvailableNotice>
          Changing your password isn't available yet — the backend has no password-change
          endpoint.
        </NotAvailableNotice>
      </Card>

      <Card>
        <Card.Header title="Account information" />
        <div className="profile-section">
          <div className="profile-field">
            <span className="text-label">Account created</span>
            <NotAvailableNotice>
              Not shown here — although the backend records this internally, it isn't included
              in the sign-in or registration response, so the frontend has no confirmed way to
              read it yet.
            </NotAvailableNotice>
          </div>
          <div className="profile-field">
            <span className="text-label">Last login</span>
            <NotAvailableNotice>Not tracked by the backend.</NotAvailableNotice>
          </div>
        </div>
      </Card>
    </PageContainer>
  );
}
