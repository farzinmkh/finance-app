import { apiFetch } from "./apiClient";

/**
 * Auth API contract (matches application/use_cases/auth/*.py on the backend):
 *
 *   POST /auth/register  { email, password }        -> { user_id, email }
 *   POST /auth/login     { email, password }         -> { access_token, token_type, user: { user_id, email } }
 *
 * The backend's LoginUser/RegisterUser use cases and the HS256 JWT
 * implementation (infrastructure/security/jwt.py) are already built; the
 * auth router itself is not in this codebase yet. These paths and shapes
 * are the expected contract — confirm against the real router once it
 * exists, and adjust this file only (nothing else depends on the shape).
 */

export function login({ email, password }) {
  return apiFetch("/auth/login", { method: "POST", body: { email, password } });
}

export function register({ email, password }) {
  return apiFetch("/auth/register", { method: "POST", body: { email, password } });
}
