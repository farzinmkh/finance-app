import { useState } from "react";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { ACCOUNT_TYPE_OPTIONS } from "./accountTypeConfig";
import { validateAccountForm, hasErrors } from "../../utils/validateAccountForm";
import "./AccountForm.css";

/**
 * <AccountForm mode="create|edit" initialValues={...} submitting onSubmit onCancel />
 *
 * Currency and opening balance are only editable on create — the backend's
 * UpdateAccountRequest has no fields for either (update_account.py explains
 * why: currency would require re-expressing historical transactions, and
 * opening_balance is part of the balance invariant current_balance =
 * opening_balance + income - expenses). Both are shown disabled in edit
 * mode rather than hidden, so the person can see the account's original
 * starting point.
 */
export function AccountForm({ mode = "create", initialValues, submitting = false, onSubmit, onCancel }) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const isEdit = mode === "edit";

  function setField(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const validationErrors = validateAccountForm(values, { isEdit });
    setErrors(validationErrors);
    if (hasErrors(validationErrors)) return;
    onSubmit(values);
  }

  return (
    <form className="account-form" onSubmit={handleSubmit} noValidate>
      <Input
        label="Account name"
        placeholder="e.g. HSBC Checking"
        value={values.name}
        onChange={(e) => setField("name", e.target.value)}
        error={errors.name}
      />

      <Select
        label="Account type"
        options={ACCOUNT_TYPE_OPTIONS}
        value={values.accountType}
        onChange={(e) => setField("accountType", e.target.value)}
        error={errors.accountType}
      />

      <div className="account-form__row">
        <Input
          label="Currency"
          placeholder="USD"
          maxLength={3}
          value={values.currency}
          onChange={(e) => setField("currency", e.target.value.toUpperCase())}
          error={errors.currency}
          disabled={isEdit}
          hint={isEdit ? "Can't be changed after creation." : "3-letter ISO code, e.g. USD, EUR, GBP."}
        />
        <Input
          label="Opening balance"
          inputMode="decimal"
          placeholder="0.00"
          value={values.openingBalance}
          onChange={(e) => setField("openingBalance", e.target.value)}
          error={errors.openingBalance}
          disabled={isEdit}
          hint={isEdit ? "Can't be changed after creation." : "Use a negative value for an existing credit balance."}
        />
      </div>

      <Modal.Footer>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" loading={submitting}>
          {isEdit ? "Save changes" : "Add account"}
        </Button>
      </Modal.Footer>
    </form>
  );
}
