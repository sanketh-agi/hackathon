import { useState } from "react";
import { HashRouter, Route, Routes, Navigate, useLocation, useNavigate } from "react-router-dom";
import CustomerSetup from "./pages/CustomerSetup";
import Documents from "./pages/Documents";
import TestCases from "./pages/TestCases";
import Reports from "./pages/Reports";
import type { Customer } from "./api/client";
import { useTheme } from "./useTheme";

const NAV_ITEMS = [
  { to: "/", label: "Customer" },
  { to: "/documents", label: "Documents" },
  { to: "/test-cases", label: "Test Cases" },
  { to: "/reports", label: "Reports" },
];

/** Visual-only tabs + prev/next pager. Pages are reached ONLY via the pager;
    the tabs show where you are but are not clickable. On the final page, Next
    becomes "Start over" and returns to the Customer page after confirmation. */
function Pager() {
  const location = useLocation();
  const navigate = useNavigate();
  const [confirmOpen, setConfirmOpen] = useState(false);

  const index = Math.max(
    0,
    NAV_ITEMS.findIndex((item) => item.to === location.pathname)
  );
  const prev = NAV_ITEMS[index - 1];
  const next = NAV_ITEMS[index + 1];
  const isLast = index === NAV_ITEMS.length - 1;

  const startOver = () => {
    setConfirmOpen(false);
    navigate("/");
  };

  return (
    <>
      <div className="pager">
        <button
          className="btn btn-secondary pager-btn"
          onClick={() => prev && navigate(prev.to)}
          disabled={!prev}
        >
          ← Previous
        </button>
        <span className="pager-progress">
          Step {index + 1} of {NAV_ITEMS.length}
        </span>
        {isLast ? (
          <button className="btn btn-primary pager-btn" onClick={() => setConfirmOpen(true)}>
            Start over ↺
          </button>
        ) : (
          <button className="btn btn-primary pager-btn" onClick={() => next && navigate(next.to)}>
            Next →
          </button>
        )}
      </div>

      {confirmOpen && (
        <div className="modal-overlay" onClick={() => setConfirmOpen(false)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="modal-title" id="confirm-title">
              Start over?
            </h3>
            <p className="modal-body">
              You've reached the end of the workflow. Return to the Customer page to begin again
              with another customer?
            </p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setConfirmOpen(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={startOver}>
                Go to Customer page
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function Tabs() {
  const location = useLocation();
  return (
    <nav className="topbar-nav" aria-label="Progress steps">
      {NAV_ITEMS.map((item) => (
        <span
          key={item.to}
          className={`nav-link${location.pathname === item.to ? " active" : ""}`}
          aria-current={location.pathname === item.to ? "page" : undefined}
        >
          {item.label}
        </span>
      ))}
    </nav>
  );
}

function Shell() {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [theme, toggleTheme] = useTheme();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-mark">AI</span>
            <span className="brand-text">Test Case Generator</span>
          </div>
          <div className="topbar-right">
            <Tabs />
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? "☀" : "☾"}
            </button>
          </div>
        </div>
        {customer && (
          <div className="customer-banner">
            <span className="dot" />
            Active customer: <strong style={{ color: "var(--text)" }}>{customer.name}</strong>
          </div>
        )}
      </header>

      <main className="container">
        <Routes>
          <Route
            path="/"
            element={
              <CustomerSetup
                customer={customer}
                onSelect={setCustomer}
                onDeleted={(id) => setCustomer((cur) => (cur?.id === id ? null : cur))}
              />
            }
          />
          <Route
            path="/documents"
            element={customer ? <Documents customer={customer} /> : <Navigate to="/" />}
          />
          <Route
            path="/test-cases"
            element={customer ? <TestCases customer={customer} /> : <Navigate to="/" />}
          />
          <Route
            path="/reports"
            element={customer ? <Reports customer={customer} /> : <Navigate to="/" />}
          />
        </Routes>

        <Pager />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <HashRouter>
      <Shell />
    </HashRouter>
  );
}
