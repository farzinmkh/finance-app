const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateEmail(email) {
  if (!email.trim()) return "Email is required.";
  if (!EMAIL_PATTERN.test(email.trim())) return "Enter a valid email address.";
  return undefined;
}

export function validateLoginForm({ email, password }) {
  const errors = {};
  const emailError = validateEmail(email);
  if (emailError) errors.email = emailError;
  if (!password) errors.password = "Password is required.";
  return errors;
}

/**
 * Password length mirrors the backend's own rule exactly
 * (RegisterUser.execute: "Password must be at least 8 characters.") so the
 * person sees it before round-tripping to the API. Confirm-password has no
 * backend counterpart — it's pure client-side protection against typos.
 */
export function validateRegisterForm({ email, password, confirmPassword }) {
  const errors = {};
  const emailError = validateEmail(email);
  if (emailError) errors.email = emailError;

  if (!password) {
    errors.password = "Password is required.";
  } else if (password.length < 8) {
    errors.password = "Password must be at least 8 characters.";
  }

  if (!errors.password && password !== confirmPassword) {
    errors.confirmPassword = "Passwords don't match.";
  }

  return errors;
}

export function hasErrors(errors) {
  return Object.keys(errors).length > 0;
}
