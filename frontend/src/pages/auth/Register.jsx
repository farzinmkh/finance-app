import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "./AuthLayout";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";
import { ApiError } from "../../services/apiClient";
import { validateRegisterForm, hasErrors } from "../../utils/validateAuthForm";
import "./AuthForm.css";

/**
 * No "Name" field: RegisterUserInput (application/use_cases/auth/
 * auth_use_cases.py) only accepts email and password, and the User domain
 * entity has no name field at all. Asking for a name here and silently
 * discarding it would be actively misleading, so it's omitted rather than
 * invented. Confirm Password has no backend counterpart either — it's
 * pure client-side protection against typos, never sent to the API.
 */
export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError(null);

    const errors = validateRegisterForm({ email, password, confirmPassword });
    setFieldErrors(errors);
    if (hasErrors(errors)) return;

    setLoading(true);
    try {
      await register(email, password);
      addToast({
        variant: "success",
        title: "Account created",
        description: "You can now sign in with your new account.",
      });
      navigate("/login", { replace: true });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message || "Couldn't create your account."
          : "Couldn't reach the server. Please try again.";
      setFormError(message);
      addToast({ variant: "error", title: "Registration failed", description: message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Create an account" subtitle="Start tracking your finances in a few seconds.">
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <Input
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={fieldErrors.email}
        />
        <Input
          label="Password"
          type="password"
          name="password"
          autoComplete="new-password"
          hint={!fieldErrors.password ? "At least 8 characters." : undefined}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fieldErrors.password}
        />
        <Input
          label="Confirm password"
          type="password"
          name="confirmPassword"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          error={fieldErrors.confirmPassword || formError}
        />
        <Button type="submit" loading={loading} className="auth-form__submit">
          Create account
        </Button>
      </form>
      <p className="text-secondary auth-form__footer">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  );
}
