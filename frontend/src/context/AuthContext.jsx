import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import * as authService from "../services/authService";
import { getStoredToken, setStoredToken, UNAUTHORIZED_EVENT } from "../services/apiClient";

export const AuthContext = createContext(null);

const USER_STORAGE_KEY = "finance-app:user";

function readStoredUser() {
  try {
    const raw = window.localStorage.getItem(USER_STORAGE_KEY) || window.sessionStorage.getItem(USER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setStoredUser(user, { remember = true } = {}) {
  window.localStorage.removeItem(USER_STORAGE_KEY);
  window.sessionStorage.removeItem(USER_STORAGE_KEY);
  if (user) {
    (remember ? window.localStorage : window.sessionStorage).setItem(USER_STORAGE_KEY, JSON.stringify(user));
  }
}

/**
 * Frontend authentication boundary.
 *
 * There is no "/auth/me" endpoint on the backend to verify a stored token,
 * so `isAuthenticated` reflects "a token is present" rather than a
 * server-verified session. A request made with an expired/invalid token is
 * rejected by the backend's own auth dependency (presentation/api/
 * dependencies.py) with 401; apiClient.js dispatches UNAUTHORIZED_EVENT on
 * every 401 it sees, and the listener below clears the stale session so
 * ProtectedRoute (already built in Phase 2) redirects to /login on its own
 * — no separate imperative navigation needed here.
 *
 * Provides:
 *   user             — { user_id, email } | null
 *   isAuthenticated  — boolean
 *   isInitializing   — true only for the first synchronous read on mount
 *   login(email, password, { remember })
 *   register(email, password)
 *   logout()
 */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken);
  const [user, setUser] = useState(readStoredUser);

  const persistSession = useCallback((nextToken, nextUser, options) => {
    setToken(nextToken);
    setUser(nextUser);
    setStoredToken(nextToken, options);
    setStoredUser(nextUser, options);
  }, []);

  const login = useCallback(
    async (email, password, { remember = true } = {}) => {
      const result = await authService.login({ email, password });
      persistSession(result.access_token, result.user ?? { email }, { remember });
      return result;
    },
    [persistSession]
  );

  const register = useCallback(async (email, password) => {
    return authService.register({ email, password });
  }, []);

  const logout = useCallback(() => {
    persistSession(null, null, { remember: true });
  }, [persistSession]);

  // A 401 from any API call means the current token is no longer valid
  // (expired, tampered, or the account no longer exists) — clear it so the
  // person lands back on /login instead of seeing broken protected pages.
  useEffect(() => {
    function handleUnauthorized() {
      persistSession(null, null, { remember: true });
    }
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [persistSession]);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(token),
      isInitializing: false,
      login,
      register,
      logout,
    }),
    [user, token, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
