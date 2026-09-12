import { useState } from "react";
import { Trash2, Inbox, MoreHorizontal, ArrowRight } from "lucide-react";
import {
  Button,
  Input,
  Textarea,
  Select,
  Card,
  Badge,
  Avatar,
  Modal,
  Drawer,
  Dropdown,
  Tabs,
  Skeleton,
  ConfirmDialog,
  EmptyState,
  ErrorState,
} from "../components/ui";
import { useToast } from "../hooks/useToast";
import "./Home.css";

/**
 * Foundation showcase for Phase 1.
 * This is a scaffolding/reference page, not a real app screen — it exists
 * so every base component and token can be seen and verified in one place
 * before Dashboard, Transactions, Accounts, etc. are built in later phases.
 */
export default function Home() {
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const { addToast } = useToast();

  return (
    <div className="container home">
      <section className="home__intro">
        <p className="text-label home__eyebrow">Phase 1 — Frontend foundation</p>
        <h1 className="text-page-title">Design system &amp; base components</h1>
        <p className="text-secondary home__lead">
          This page is a working reference for the tokens and primitives set
          up in this phase. Dashboard, Transactions, Accounts, and other real
          screens come in later phases.
        </p>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Typography</h2>
        <Card>
          <div className="home__type-scale">
            <p className="text-page-title">Page title</p>
            <p className="text-section-title">Section title</p>
            <p className="text-card-title">Card title</p>
            <p className="text-body">Body text — the default paragraph style.</p>
            <p className="text-secondary">Secondary text — for supporting detail.</p>
            <p className="text-label">Label text</p>
            <p className="text-caption">Caption text</p>
          </div>
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Colors</h2>
        <div className="home__swatches">
          {[
            ["Background", "var(--color-bg)"],
            ["Surface", "var(--color-surface)"],
            ["Primary", "var(--color-primary)"],
            ["Text", "var(--color-text)"],
            ["Secondary text", "var(--color-text-secondary)"],
            ["Border", "var(--color-border)"],
            ["Income", "var(--color-income)"],
            ["Expense", "var(--color-expense)"],
            ["Warning", "var(--color-warning)"],
          ].map(([label, color]) => (
            <div className="swatch" key={label}>
              <span className="swatch__chip" style={{ backgroundColor: color }} />
              <span className="text-caption">{label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Buttons</h2>
        <Card>
          <div className="home__row">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
            <Button variant="primary" loading>
              Saving
            </Button>
            <Button variant="secondary" iconOnly aria-label="More options">
              <MoreHorizontal size={16} />
            </Button>
          </div>
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Form fields</h2>
        <Card>
          <div className="home__form-grid">
            <Input label="Account name" placeholder="e.g. HSBC Checking" />
            <Select
              label="Account type"
              placeholder="Choose a type"
              options={[
                { value: "checking", label: "Checking" },
                { value: "savings", label: "Savings" },
                { value: "credit", label: "Credit" },
              ]}
            />
            <Input label="Opening balance" placeholder="0.00" error="Amount is required" />
            <Textarea label="Notes" placeholder="Optional notes about this account" />
          </div>
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Badges &amp; avatars</h2>
        <Card>
          <div className="home__row">
            <Badge tone="neutral">Neutral</Badge>
            <Badge tone="primary">Primary</Badge>
            <Badge tone="income">Income</Badge>
            <Badge tone="expense">Expense</Badge>
            <Badge tone="warning">Warning</Badge>
            <Avatar name="Farzin K." size="sm" />
            <Avatar name="Ada Lovelace" size="md" />
            <Avatar name="Grace Hopper" size="lg" />
          </div>
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Tabs</h2>
        <Card>
          <Tabs
            items={[
              { value: "overview", label: "Overview", content: <p className="text-secondary">Overview panel content.</p> },
              { value: "activity", label: "Activity", content: <p className="text-secondary">Activity panel content.</p> },
              { value: "settings", label: "Settings", content: <p className="text-secondary">Settings panel content.</p> },
            ]}
          />
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Overlays &amp; feedback</h2>
        <Card>
          <div className="home__row">
            <Button onClick={() => setModalOpen(true)}>Open modal</Button>
            <Button variant="secondary" onClick={() => setDrawerOpen(true)}>
              Open drawer
            </Button>
            <Button variant="danger" onClick={() => setConfirmOpen(true)}>
              Open confirm dialog
            </Button>
            <Dropdown
              trigger={<Button variant="secondary">Row actions</Button>}
              align="start"
            >
              <Dropdown.Item>Edit</Dropdown.Item>
              <Dropdown.Item tone="danger">
                <Trash2 size={14} /> Delete
              </Dropdown.Item>
            </Dropdown>
            <Button
              variant="secondary"
              onClick={() =>
                addToast({
                  variant: "success",
                  title: "Saved",
                  description: "Your changes were saved.",
                })
              }
            >
              Show toast
            </Button>
          </div>
        </Card>
      </section>

      <section className="home__section">
        <h2 className="text-section-title">Loading &amp; empty states</h2>
        <div className="home__grid-3">
          <Card>
            <div className="home__skeleton-stack">
              <Skeleton width="60%" height={14} />
              <Skeleton width="90%" height={14} />
              <Skeleton width="40%" height={14} />
            </div>
          </Card>
          <Card>
            <EmptyState
              icon={<Inbox size={22} />}
              title="No transactions yet"
              description="Once you add one, it'll show up here."
              action={
                <Button size="sm" variant="secondary">
                  Add transaction
                </Button>
              }
            />
          </Card>
          <Card>
            <ErrorState
              description="Check your connection and try again."
              action={
                <Button size="sm" variant="secondary">
                  Retry <ArrowRight size={14} />
                </Button>
              }
            />
          </Card>
        </div>
      </section>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Example modal"
        description="Used for focused tasks like creating or editing a record."
      >
        <p className="text-secondary">Modal body content goes here.</p>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => setModalOpen(false)}>Save</Button>
        </Modal.Footer>
      </Modal>

      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Example drawer">
        <p className="text-secondary">Drawers are useful for filters or secondary panels.</p>
      </Drawer>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete this item?"
        description="This action cannot be undone."
        confirmLabel="Delete"
        tone="danger"
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => setConfirmOpen(false)}
      />
    </div>
  );
}
