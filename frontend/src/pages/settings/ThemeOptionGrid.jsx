import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "../../hooks/useTheme";
import { cn } from "../../utils/cn";
import "./ThemeOptionGrid.css";

const OPTIONS = [
  { value: "light", label: "Light", description: "Always use the light theme.", Icon: Sun },
  { value: "dark", label: "Dark", description: "Always use the dark theme.", Icon: Moon },
  { value: "system", label: "System", description: "Match your device's setting.", Icon: Monitor },
];

/**
 * A more spelled-out version of the Topbar's compact ThemeToggle, better
 * suited to a Settings page where each option deserves a visible label.
 * Both read from the same ThemeContext, so choosing here or in the Topbar
 * always stays in sync.
 */
export function ThemeOptionGrid() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="theme-option-grid" role="radiogroup" aria-label="Theme">
      {OPTIONS.map(({ value, label, description, Icon }) => (
        <button
          key={value}
          type="button"
          role="radio"
          aria-checked={theme === value}
          className={cn("theme-option", theme === value && "theme-option--active")}
          onClick={() => setTheme(value)}
        >
          <Icon size={18} aria-hidden="true" />
          <span className="theme-option__label text-label">{label}</span>
          <span className="theme-option__description text-caption">{description}</span>
        </button>
      ))}
    </div>
  );
}
