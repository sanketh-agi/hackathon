import { useEffect, useState } from "react";
import { api, type Customer, type TestCase, type TestRun } from "../api/client";

const RUN_BADGE: Record<string, string> = {
  passed: "badge-success",
  failed: "badge-danger",
  running: "badge-info",
  pending: "badge-neutral",
};

export default function Runs({ customer }: { customer: Customer }) {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [runsByTestCase, setRunsByTestCase] = useState<Record<number, TestRun[]>>({});
  const [running, setRunning] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    const cases = await api.listTestCases(customer.id);
    const approved = cases.filter((c) => c.status === "approved");
    setTestCases(approved);
    const runs: Record<number, TestRun[]> = {};
    for (const c of approved) {
      runs[c.id] = await api.listRuns(c.id).catch(() => []);
    }
    setRunsByTestCase(runs);
  };

  useEffect(() => {
    refresh().catch((e) => setError(String(e)));
  }, [customer.id]);

  const run = async (id: number) => {
    setRunning(id);
    setError(null);
    try {
      await api.runTestCase(id);
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Runs</h2>
          <p className="page-subtitle">Execute approved test cases against {customer.app_url || "the configured application URL"}.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {testCases.length === 0 ? (
        <div className="empty-state">No approved test cases yet. Approve one from the Test Cases page first.</div>
      ) : (
        testCases.map((tc) => (
          <div key={tc.id} className="test-case">
            <div className="test-case-header">
              <span className="test-case-title">{tc.title}</span>
              <button className="btn btn-primary btn-sm" onClick={() => run(tc.id)} disabled={running === tc.id}>
                {running === tc.id ? (
                  <>
                    <span className="spinner" /> Running...
                  </>
                ) : (
                  "Run"
                )}
              </button>
            </div>

            {(runsByTestCase[tc.id] || []).length === 0 ? (
              <p className="status-note">Not run yet.</p>
            ) : (
              <div className="table-scroll">
                <table className="data-table" style={{ marginTop: "0.5rem" }}>
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Started</th>
                      <th>Finished</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(runsByTestCase[tc.id] || []).map((r) => (
                      <tr key={r.id}>
                        <td>
                          <span
                            className={`badge ${RUN_BADGE[r.status] ?? "badge-neutral"}${
                              r.status === "running" ? " badge-pulse" : ""
                            }`}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td>{new Date(r.started_at).toLocaleString()}</td>
                        <td>{r.finished_at ? new Date(r.finished_at).toLocaleString() : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
