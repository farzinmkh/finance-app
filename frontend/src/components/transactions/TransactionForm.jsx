import { useState } from "react";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { Textarea } from "../ui/Textarea";
import { Button } from "../ui/Button";
import { Modal } from "../ui/Modal";
import { validateTransactionForm, hasErrors } from "../../utils/validateTransactionForm";
import "./TransactionForm.css";

const TYPE_TABS = [
  { value: "expense", label: "Expense" },
  { value: "income", label: "Income" },
  { value: "transfer", label: "Transfer" },
];

/**
 * <TransactionForm
 *   mode="create|edit"
 *   initialValues={buildInitialValues(...)}
 *   accounts={accounts} categories={categories}
 *   accountLocked={mode === "edit"}   // backend forbids changing account_id on update
 *   submitting={isSubmitting}
 *   onSubmit={(values) => ...}
 *   onCancel={() => ...}
 * />
 *
 * Pure form: no fetching, no modal chrome. `onSubmit` receives validated
 * field values; the caller (TransactionFormModal) maps them to the exact
 * service-call shape and handles success/close/toast.
 */
export function TransactionForm({
  mode = "create",
  initialValues,
  accounts,
  categories,
  accountLocked = false,
  submitting = false,
  onSubmit,
  onCancel,
}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});

  const availableTypes = mode === "edit" ? TYPE_TABS.filter((t) => t.value !== "transfer") : TYPE_TABS;
  const categoryOptions = categories
    .filter((c) => c.category_type === values.type)
    .map((c) => ({ value: c.id, label: c.name }));
  const accountOptions = accounts.map((a) => ({ value: a.id, label: a.name }));

  function setField(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  function handleTypeChange(type) {
    // Category only applies to expense/income and must match the new type,
    // and switching to/from transfer clears fields that no longer apply.
    setValues((prev) => ({
      ...prev,
      type,
      categoryId: "",
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const validationErrors = validateTransactionForm(values);
    setErrors(validationErrors);
    if (hasErrors(validationErrors)) return;
    onSubmit(values);
  }

  return (
    <form className="transaction-form" onSubmit={handleSubmit} noValidate>
      <div className="transaction-form__type-tabs" role="radiogroup" aria-label="Transaction type">
        {availableTypes.map((tab) => (
          <button
            key={tab.value}
            type="button"
            role="radio"
            aria-checked={values.type === tab.value}
            className={`transaction-form__type-tab transaction-form__type-tab--${tab.value}${
              values.type === tab.value ? " transaction-form__type-tab--active" : ""
            }`}
            onClick={() => handleTypeChange(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <Input
        label="Amount"
        inputMode="decimal"
        placeholder="0.00"
        value={values.amount}
        onChange={(e) => setField("amount", e.target.value)}
        error={errors.amount}
        startAdornment="$"
      />

      {values.type === "transfer" ? (
        <div className="transaction-form__row">
          <Select
            label="Source account"
            placeholder="Choose an account"
            options={accountOptions}
            value={values.fromAccountId}
            onChange={(e) => setField("fromAccountId", e.target.value)}
            error={errors.fromAccountId}
          />
          <Select
            label="Destination account"
            placeholder="Choose an account"
            options={accountOptions}
            value={values.toAccountId}
            onChange={(e) => setField("toAccountId", e.target.value)}
            error={errors.toAccountId}
          />
        </div>
      ) : (
        <div className="transaction-form__row">
          <Select
            label="Account"
            placeholder="Choose an account"
            options={accountOptions}
            value={values.accountId}
            onChange={(e) => setField("accountId", e.target.value)}
            error={errors.accountId}
            disabled={accountLocked}
            hint={accountLocked ? "The account can't be changed after creation." : undefined}
          />
          <Select
            label="Category"
            placeholder="Uncategorized"
            options={categoryOptions}
            value={values.categoryId}
            onChange={(e) => setField("categoryId", e.target.value)}
            error={errors.categoryId}
          />
        </div>
      )}

      <div className="transaction-form__row">
        <Input
          label="Date"
          type="date"
          value={values.date}
          onChange={(e) => setField("date", e.target.value)}
          error={errors.date}
        />
      </div>

      <Textarea
        label="Description"
        placeholder="Optional notes about this transaction"
        value={values.notes}
        onChange={(e) => setField("notes", e.target.value)}
        error={errors.notes}
        rows={3}
      />

      <Modal.Footer>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" loading={submitting}>
          {mode === "edit" ? "Save changes" : "Add transaction"}
        </Button>
      </Modal.Footer>
    </form>
  );
}
