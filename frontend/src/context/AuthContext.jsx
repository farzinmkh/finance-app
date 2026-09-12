import { createContext, useCallback, useMemo, useState } from "react";
import * as authService from "../services/authService";
import { getStoredToken, setStoredToken } from "../services/apiClient";

export const AuthContext = createContext(null);

const USER_STORAGE_KEY = "finance-app:user";

function readStoredUser() {
  try {
    const raw = window.localStorage.getItem(USER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Frontend authentication boundary.
 *
 * There is no "/auth/me" endpoint on the backend to verify a stored token,
 * so `isAuthenticated` reflects "a token is present" rather than a
 * server-verified session. Any request made with an expired/invalid token
 * will still be rejected by the backend's own auth dependency
 * (see presentation/api/dependencies.py) and should trigger `logout()`
 * from the API layer once real requests are wired up.
 *
 * Provides:
 *   user             — { user_id, email } | null
 *   isAuthenticated  — boolean
 *   isInitializing   — true only for the first synchronous read on mount
 *   login(email, password)
 *   register(email, password)
 *   logout()
 */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken);
  const [user, setUser] = useState(readStoredUser);

  const persistSession = useCallback((nextToken, nextUser) => {
    setToken(nextToken);
    setUser(nextUser);
    setStoredToken(nextToken);
    if (nextUser) {
      window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser));
    } else {
      window.localStorage.removeItem(USER_STORAGE_KEY);
    }
  }, []);

  const login = useCallback(
    async (email, password) => {
      const result = await authService.login({ email, password });
      persistSession(result.access_token, result.user ?? { email });
      return result;
    },
    [persistSession]
  );

  const register = useCallback(async (email, password) => {
    return authService.register({ email, password });
  }, []);

  const logout = useCallback(() => {
    persistSession(null, null);
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
