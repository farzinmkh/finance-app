import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import { ToastProvider } from "./context/ToastContext";
import { AuthProvider } from "./context/AuthContext";
import { ToastViewport } from "./components/ui";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ProtectedRoute, GuestRoute } from "./components/ProtectedRoute";
import { AppShell } from "./components/layout/AppShell";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import RoutePlaceholder from "./pages/RoutePlaceholder";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import NotFound from "./pages/NotFound";
import Home from "./pages/Home";

/**
 * Phase 2 routing map.
 *
 *   /login, /register        — public, redirect away if already signed in
 *   /dashboard ... /profile  — protected, rendered inside AppShell
 *   /style-guide             — Phase 1 component reference (unprotected, not in nav)
 *   /404, *                  — not found
 *
 * Real page functionality (Dashboard, Transactions, Accounts, Analytics,
 * Settings, Profile) is built in later phases — each route currently
 * renders RoutePlaceholder so navigation, guards, and layout can be
 * verified end-to-end without inventing business logic.
 */
export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* Public, pre-authentication routes */}
                <Route element={<GuestRoute />}>
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                </Route>

                {/* Phase 1 design-system reference, not part of the app nav */}
                <Route path="/style-guide" element={<Home />} />

                {/* Protected application routes */}
                <Route element={<ProtectedRoute />}>
                  <Route element={<AppShell />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route
                      path="/accounts"
                      element={<RoutePlaceholder title="Accounts" />}
                    />
                    <Route
                      path="/analytics"
                      element={<RoutePlaceholder title="Analytics" />}
                    />
                    <Route
                      path="/settings"
                      element={<RoutePlaceholder title="Settings" />}
                    />
                    <Route
                      path="/profile"
                      element={<RoutePlaceholder title="Profile" />}
                    />
                  </Route>
                </Route>

                <Route path="/404" element={<NotFound />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
            <ToastViewport />
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
