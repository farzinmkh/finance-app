/**
 * The confirmed /transactions API has no `search` or `sort` query param
 * (see services/transactionService.js), so both are applied here, in the
 * browser, over whatever page is currently loaded. This means search only
 * finds matches on the current page — increasing page size reduces how
 * often that's surprising, but it's an honest tradeoff until the backend
 * adds real params, not a silent limitation.
 */
export function applySearchAndSort(items, { search, sort, categoriesById }) {
  let result = items;

  const term = search?.trim().toLowerCase();
  if (term) {
    result = result.filter((tx) => {
      const categoryName = categoriesById.get(tx.category_id)?.name || "";
      return (
        tx.notes?.toLowerCase().includes(term) ||
        categoryName.toLowerCase().includes(term)
      );
    });
  }

  if (sort) {
    const { field, direction } = sort;
    const dir = direction === "asc" ? 1 : -1;
    result = [...result].sort((a, b) => {
      if (field === "amount") return (Number(a.amount) - Number(b.amount)) * dir;
      if (field === "date") return (new Date(a.date) - new Date(b.date)) * dir;
      if (field === "notes") return (a.notes || "").localeCompare(b.notes || "") * dir;
      return 0;
    });
  }

  return result;
}
