import { Construction } from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { EmptyState } from "../components/ui/EmptyState";
import "./RoutePlaceholder.css";

/**
 * Used for every protected route until its real page is built in a later
 * phase (Dashboard, Transactions, Accounts, Analytics, Settings, Profile).
 * Confirms the route, layout, and navigation all work end-to-end without
 * inventing any business functionality or fake data.
 */
export default function RoutePlaceholder({ title, description }) {
  return (
    <PageContainer>
      <div className="route-placeholder">
        <EmptyState
          icon={<Construction size={22} />}
          title={title}
          description={description || `The ${title} page is coming in a later phase.`}
        />
      </div>
    </PageContainer>
  );
}
