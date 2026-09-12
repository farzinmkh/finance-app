import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

/**
 * Guards a branch of routes behind authentication. Unauthenticated visitors
 * are redirected to /login with the originally requested location preserved
 * in state, so Login can send them back after a successful sign-in.
 *
 * Usage:
 *   <Route element={<ProtectedRoute />}>
 *     <Route element={<AppShell />}>
 *       <Route path="/dashboard" element={<... />} />
 *     </Route>
 *   </Route>
 */
export function ProtectedRoute() {
  const { isAuthenticated, isInitializing } = useAuth();
  const location = useLocation();

  if (isInitializing) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

/**
 * Inverse guard for /login and /register: an already-authenticated visitor
 * is sent straight to the app instead of seeing the auth forms again.
 */
export function GuestRoute() {
  const { isAuthenticated, isInitializing } = useAuth();

  if (isInitializing) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
