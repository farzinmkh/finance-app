import { TrendingUp, TrendingDown } from "lucide-react";
import { Card } from "../ui/Card";
import { Skeleton } from "../ui/Skeleton";
import { cn } from "../../utils/cn";
import "./StatCard.css";

/**
 * <StatCard
 *   icon={Wallet}
 *   tone="primary|income|expense|warning"
 *   title="Total Balance"
 *   amount="$18,420.35"
 *   secondary="3 accounts"
 *   trend={{ direction: "up", positive: true, label: "5.0% vs last month" }}
 *   loading={false}
 * />
 *
 * `trend.direction` controls which arrow is shown; `trend.positive` controls
 * its color — the two are independent because "up" isn't always good (e.g.
 * rising expenses should read as unfavorable even though the arrow points up).
 * `trend` is optional — omit it when the metric has no prior-period
 * comparison (e.g. Total Balance has no "trend" in the assumed contract).
 */
export function StatCard({ icon: Icon, tone = "primary", title, amount, secondary, trend, loading = false }) {
  return (
    <Card className="stat-card">
      <div className={cn("stat-card__icon", `stat-card__icon--${tone}`)}>
        <Icon size={18} aria-hidden="true" />
      </div>

      <p className="stat-card__title text-label">{title}</p>

      {loading ? (
        <>
          <Skeleton width="70%" height={26} />
          <Skeleton width="45%" height={14} style={{ marginTop: 8 }} />
        </>
      ) : (
        <>
          <p className="stat-card__amount text-mono">{amount}</p>
          <div className="stat-card__footer">
            {secondary && <span className="stat-card__secondary text-caption">{secondary}</span>}
            {trend && (
              <span
                className={cn(
                  "stat-card__trend",
                  trend.positive === true && "stat-card__trend--positive",
                  trend.positive === false && "stat-card__trend--negative"
                )}
              >
                {trend.direction === "up" && <TrendingUp size={12} aria-hidden="true" />}
                {trend.direction === "down" && <TrendingDown size={12} aria-hidden="true" />}
                {trend.label}
              </span>
            )}
          </div>
        </>
      )}
    </Card>
  );
}
