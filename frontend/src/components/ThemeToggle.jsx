import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "../hooks/useTheme";
import "./ThemeToggle.css";

const OPTIONS = [
  { value: "light", label: "Light", Icon: Sun },
  { value: "dark", label: "Dark", Icon: Moon },
  { value: "system", label: "System", Icon: Monitor },
];

/** Segmented control for choosing the app's color theme. */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="theme-toggle" role="radiogroup" aria-label="Color theme">
      {OPTIONS.map(({ value, label, Icon }) => (
        <button
          key={value}
          type="button"
          role="radio"
          aria-checked={theme === value}
          aria-label={label}
          title={label}
          className={`theme-toggle__option${theme === value ? " theme-toggle__option--active" : ""}`}
          onClick={() => setTheme(value)}
        >
          <Icon size={15} aria-hidden="true" />
        </button>
      ))}
    </div>
  );
}
