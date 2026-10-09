import { useEffect, useState } from "react";
import { api, type Customer } from "../api/client";

export default function CustomerSetup({
  customer,
  onSelect,
  onDeleted,
}: {
  customer: Customer | null;
  onSelect: (c: Customer) => void;
  onDeleted?: (id: number) => void;
}) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Customer | null>(null);
  const [deleting, setDeleting] = useState(false);

  const refresh = () => api.listCustomers().then(setCustomers).catch((e) => setError(String(e)));

  useEffect(() => {
    refresh();
  }, []);

  const create = async () => {
    setError(null);
    try {
      const created = await api.createCustomer({ name });
      setCustomers((prev) => [created, ...prev]);
      onSelect(created);
      setName("");
    } catch (e) {
      setError(String(e));
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setError(null);
    try {
      await api.deleteCustomer(pendingDelete.id);
      setCustomers((prev) => prev.filter((c) => c.id !== pendingDelete.id));
      onDeleted?.(pendingDelete.id);
      setPendingDelete(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setDeleting(false);
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
              <div className="customer-row" key={c.id}>
                <button
                  className={`btn-list${customer?.id === c.id ? " selected" : ""}`}
                  onClick={() => onSelect(c)}
                >
                  <span>{c.name}</span>
                </button>
                <button
                  className="icon-btn icon-btn-danger"
                  onClick={() => setPendingDelete(c)}
                  aria-label={`Delete ${c.name}`}
                  title={`Delete ${c.name}`}
                >
                  🗑
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {pendingDelete && (
        <div className="modal-overlay" onClick={() => !deleting && setPendingDelete(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-title"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="modal-title" id="delete-title">
              Delete customer?
            </h3>
            <p className="modal-body">
              This permanently deletes <strong>{pendingDelete.name}</strong> along with all its
              documents, rules, and generated test cases. This cannot be undone.
            </p>
            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setPendingDelete(null)}
                disabled={deleting}
              >
                Cancel
              </button>
              <button className="btn btn-danger" onClick={confirmDelete} disabled={deleting}>
                {deleting ? (
                  <>
                    <span className="spinner" /> Deleting…
                  </>
                ) : (
                  "Delete customer"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
