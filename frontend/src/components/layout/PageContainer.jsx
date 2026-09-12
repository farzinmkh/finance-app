import { cn } from "../../utils/cn";
import "./PageContainer.css";

/**
 * Wraps the content of every route rendered inside AppShell so spacing,
 * max-width, and heading layout stay consistent as real pages are built.
 *
 * <PageContainer title="Accounts" description="..." actions={<Button>Add account</Button>}>
 *   ...page content...
 * </PageContainer>
 *
 * `title`/`description`/`actions` are optional — Topbar already shows the
 * route's title, so most pages will only need this for the extra
 * description/actions row, or can omit the header entirely.
 */
export function PageContainer({ title, description, actions, className, children }) {
  const hasHeader = title || description || actions;

  return (
    <div className={cn("page-container", className)}>
      {hasHeader && (
        <div className="page-container__header">
          <div className="page-container__heading">
            {title && <h2 className="page-container__title text-section-title">{title}</h2>}
            {description && (
              <p className="page-container__description text-secondary">{description}</p>
            )}
          </div>
          {actions && <div className="page-container__actions">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
