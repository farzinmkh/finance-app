import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

const STORAGE_KEY = "finance-app:theme";
const THEMES = ["light", "dark", "system"];

export const ThemeContext = createContext(null);

function getSystemPrefersDark() {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function readStoredTheme() {
  if (typeof window === "undefined") return "system";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return THEMES.includes(stored) ? stored : "system";
}

/**
 * Provides `theme` (the user's preference: "light" | "dark" | "system"),
 * `resolvedTheme` (the actual applied value: "light" | "dark"), and
 * `setTheme` to the rest of the app. Persists the preference and reacts
 * to OS-level theme changes when "system" is selected.
 */
export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(readStoredTheme);
  const [systemPrefersDark, setSystemPrefersDark] = useState(getSystemPrefersDark);

  const setTheme = useCallback((next) => {
    if (!THEMES.includes(next)) return;
    setThemeState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  // Derived value — computed during render, not via setState-in-effect.
  const resolvedTheme = theme === "system" ? (systemPrefersDark ? "dark" : "light") : theme;

  // Side effect: sync the resolved theme onto the DOM. Does not call setState.
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", resolvedTheme);
    document.documentElement.style.colorScheme = resolvedTheme;
  }, [resolvedTheme]);

  // Listen for OS-level theme changes while "system" is selected.
  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (event) => setSystemPrefersDark(event.matches);
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  const value = useMemo(
    () => ({ theme, resolvedTheme, setTheme }),
    [theme, resolvedTheme, setTheme]
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
