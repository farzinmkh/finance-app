import { apiFetch } from "./apiClient";

/**
 * Confirmed contract — presentation/api/routers/categories.py (full router
 * source available). CategoryResponse: { id, name, category_type, created_at }.
 */

export function listCategories(categoryType) {
  const query = categoryType ? `?category_type=${categoryType}` : "";
  return apiFetch(`/categories${query}`);
}
