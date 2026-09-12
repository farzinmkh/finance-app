import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import { ToastProvider } from "./context/ToastContext";
import { ToastViewport } from "./components/ui";
import { AppHeader } from "./components/AppHeader";
import Home from "./pages/Home";

/**
 * Phase 1 shell: providers + router + shared header.
 * Only the foundation showcase route exists so far. Dashboard, Transactions,
 * Accounts, Analytics, Settings, and Profile pages are added in later phases.
 */
export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter>
          <div className="app-shell">
            <AppHeader />
            <main>
              <Routes>
                <Route path="/" element={<Home />} />
              </Routes>
            </main>
          </div>
        </BrowserRouter>
        <ToastViewport />
      </ToastProvider>
    </ThemeProvider>
  );
}
