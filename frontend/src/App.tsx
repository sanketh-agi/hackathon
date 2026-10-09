import { useState } from "react";
import { HashRouter, NavLink, Route, Routes, Navigate } from "react-router-dom";
import CustomerSetup from "./pages/CustomerSetup";
import Documents from "./pages/Documents";
import TestCases from "./pages/TestCases";
import Runs from "./pages/Runs";
import Reports from "./pages/Reports";
import type { Customer } from "./api/client";

const NAV_ITEMS = [
  { to: "/", label: "Customer" },
  { to: "/documents", label: "Documents" },
  { to: "/test-cases", label: "Test Cases" },
  { to: "/runs", label: "Runs" },
  { to: "/reports", label: "Reports" },
];

export default function App() {
  const [customer, setCustomer] = useState<Customer | null>(null);

  return (
    <HashRouter>
      <div className="app-shell">
        <header className="topbar">
          <div className="topbar-inner">
            <div className="brand">
              <span className="brand-mark">AI</span>
              Test Case Generator
            </div>
            <nav className="topbar-nav">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          {customer && (
            <div className="customer-banner">
              <span className="dot" />
              Active customer: <strong style={{ color: "var(--text)" }}>{customer.name}</strong>
              {customer.app_url && <span>· {customer.app_url}</span>}
            </div>
          )}
        </header>

        <main className="container">
          <Routes>
            <Route path="/" element={<CustomerSetup customer={customer} onSelect={setCustomer} />} />
            <Route
              path="/documents"
              element={customer ? <Documents customer={customer} /> : <Navigate to="/" />}
            />
            <Route
              path="/test-cases"
              element={customer ? <TestCases customer={customer} /> : <Navigate to="/" />}
            />
            <Route path="/runs" element={customer ? <Runs customer={customer} /> : <Navigate to="/" />} />
            <Route
              path="/reports"
              element={customer ? <Reports customer={customer} /> : <Navigate to="/" />}
            />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}
