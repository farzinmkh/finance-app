import { Component } from "react";
import { ErrorState } from "./ui/ErrorState";
import { Button } from "./ui/Button";
import "./ErrorBoundary.css";

/**
 * Catches render-time errors in its subtree and shows a recoverable fallback
 * instead of a blank white screen. React error boundaries must be classes.
 *
 * Wrap the whole app (see App.jsx) and, optionally, individual risky
 * sections in later phases (e.g. a chart-heavy Analytics page).
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // Replace with real error reporting (e.g. Sentry) in a later phase.
    console.error("Unhandled application error:", error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false });
    this.props.onReset?.();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <ErrorState
            title="Something went wrong"
            description="An unexpected error occurred while rendering this page. Try reloading — if it keeps happening, let us know."
            action={
              <Button onClick={() => window.location.reload()}>Reload page</Button>
            }
          />
        </div>
      );
    }

    return this.props.children;
  }
}
