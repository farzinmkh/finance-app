/**
 * Base URL for the FastAPI backend. Override via a .env file:
 *   VITE_API_BASE_URL=https://api.example.com/api/v1
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const TOKEN_STORAGE_KEY = "finance-app:token";

/** Fired whenever the API rejects a request with 401 — see AuthContext,
 * which listens for this to clear the stale session. Kept as a DOM event
 * (rather than importing AuthContext here) because this is a plain module,
 * not a component, and shouldn't depend on React context. */
export const UNAUTHORIZED_EVENT = "finance-app:unauthorized";

/**
 * The token is stored in localStorage OR sessionStorage, never both —
 * this is what "Remember me" on the login form controls (a purely
 * frontend persistence choice; the backend's own token expiry, set via
 * ACCESS_TOKEN_EXPIRE_MINUTES, is unaffected either way).
 */
export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY) || window.sessionStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token, { remember = true } = {}) {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  window.sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  if (token) {
    (remember ? window.localStorage : window.sessionStorage).setItem(TOKEN_STORAGE_KEY, token);
  }
}

/**
 * Thrown by apiFetch on any non-2xx response. Mirrors the backend's
 * consistent error shape: { error: "SOME_CODE", message: "..." }
 * (see presentation/api/error_handlers.py in the backend).
 */
export class ApiError extends Error {
  constructor(status, code, message) {
    super(message || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/**
 * Minimal fetch wrapper: attaches the Bearer token when present, parses
 * JSON, and normalises backend errors into ApiError. No endpoints beyond
 * what the backend already exposes should be called through this client.
 *
 * On 401 (expired/invalid token, per the backend's get_current_user
 * dependency), dispatches UNAUTHORIZED_EVENT so AuthContext can clear the
 * stale session — this also fires harmlessly during a failed login/register
 * attempt, where there's no valid session to clear.
 */
export async function apiFetch(path, { method = "GET", body, headers, ...rest } = {}) {
  const token = getStoredToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    ...rest,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    if (response.status === 401) {
      window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT));
    }
    throw new ApiError(response.status, data?.error, data?.message);
  }

  return data;
}
