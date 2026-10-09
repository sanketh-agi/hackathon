import { useEffect, useState } from "react";
import { api, type Customer } from "../api/client";

export default function CustomerSetup({
  customer,
  onSelect,
}: {
  customer: Customer | null;
  onSelect: (c: Customer) => void;
}) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [name, setName] = useState("");
  const [appUrl, setAppUrl] = useState("");
  const [configText, setConfigText] = useState("{}");
  const [error, setError] = useState<string | null>(null);

  const refresh = () => api.listCustomers().then(setCustomers).catch((e) => setError(String(e)));

  useEffect(() => {
    refresh();
  }, []);

  const create = async () => {
    setError(null);
    try {
      const config_json = configText.trim() ? JSON.parse(configText) : {};
      const created = await api.createCustomer({ name, app_url: appUrl, config_json });
      setCustomers((prev) => [created, ...prev]);
      onSelect(created);
      setName("");
      setAppUrl("");
      setConfigText("{}");
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Customer Setup</h2>
          <p className="page-subtitle">Create a customer profile, then select it to work with documents and test cases.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="card-header">
          <h3 className="section-title" style={{ margin: 0 }}>
            Create customer
          </h3>
        </div>
        <div className="field-group" style={{ maxWidth: 480 }}>
          <div>
            <label className="field-label">Customer name</label>
            <input className="input" placeholder="e.g. Acme Corp" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label className="field-label">Application URL</label>
            <input
              className="input"
              placeholder="https://staging.acme.com"
              value={appUrl}
              onChange={(e) => setAppUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="field-label">Customer-specific configuration (JSON)</label>
            <textarea
              className="textarea"
              value={configText}
              onChange={(e) => setConfigText(e.target.value)}
              rows={4}
            />
          </div>
          <div>
            <button className="btn btn-primary" onClick={create} disabled={!name}>
              Create customer
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="section-title" style={{ margin: 0 }}>
            Select existing customer
          </h3>
        </div>
        {customers.length === 0 ? (
          <div className="empty-state">No customers yet — create one above to get started.</div>
        ) : (
          <div style={{ display: "grid", gap: "0.25rem" }}>
            {customers.map((c) => (
              <button
                key={c.id}
                className={`btn-list${customer?.id === c.id ? " selected" : ""}`}
                onClick={() => onSelect(c)}
              >
                <span>{c.name}</span>
                <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>{c.app_url || "no URL"}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
