/**
 * Base URL for the FastAPI backend. Override via a .env file:
 *   VITE_API_BASE_URL=https://api.example.com/api/v1
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const TOKEN_STORAGE_KEY = "finance-app:token";

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token) {
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
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
    throw new ApiError(response.status, data?.error, data?.message);
  }

  return data;
}
