import { useEffect, useMemo, useState } from "react";
import { api, type Customer, type Rule, type TestCase } from "../api/client";

const PRIORITY_BADGE: Record<string, string> = {
  critical: "badge-danger",
  high: "badge-warning",
  medium: "badge-info",
  low: "badge-neutral",
};

const STATUS_BADGE: Record<string, string> = {
  draft: "badge-neutral",
  approved: "badge-success",
};

export default function TestCases({ customer }: { customer: Customer }) {
  const [rules, setRules] = useState<Rule[]>([]);
  const [search, setSearch] = useState("");
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);

  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scriptStatus, setScriptStatus] = useState<Record<number, string>>({});
  const [scripts, setScripts] = useState<Record<number, string>>({});

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    title: "",
    preconditions: "",
    steps: "",
    expected_result: "",
    priority: "medium",
  });
  const [saving, setSaving] = useState(false);

  const refreshRules = () =>
    api.listRules(customer.id).then(setRules).catch((e) => setError(String(e)));

  const refreshTestCases = async () => {
    const cases = await api.listTestCases(customer.id);
    setTestCases(cases);
    const found: Record<number, string> = {};
    await Promise.all(
      cases
        .filter((c) => c.status === "approved")
        .map((c) =>
          api
            .getScript(c.id)
            .then((s) => {
              found[c.id] = s.code;
            })
            .catch(() => {})
        )
    );
    setScripts((prev) => ({ ...prev, ...found }));
  };

  const scriptFilename = (tc: TestCase) =>
    `testcase_${tc.id}_${tc.title.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "")}.spec.ts`;

  const downloadScript = (tc: TestCase, code: string) => {
    const blob = new Blob([code], { type: "text/typescript" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = scriptFilename(tc);
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    refreshRules();
    refreshTestCases();
    setSelectedRuleId(null);
    setSearch("");
  }, [customer.id]);

  const filteredRules = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return rules;
    return rules.filter(
      (r) => r.rule_name.toLowerCase().includes(q) || r.sheet_name.toLowerCase().includes(q)
    );
  }, [rules, search]);

  const selectedRule = rules.find((r) => r.id === selectedRuleId) ?? null;

  const generate = async () => {
    if (!selectedRuleId) return;
    setGenerating(true);
    setError(null);
    try {
      await api.generateTestCases(customer.id, selectedRuleId, "");
      await refreshTestCases();
    } catch (e) {
      setError(String(e));
    } finally {
      setGenerating(false);
    }
  };

  const approve = async (id: number) => {
    await api.approveTestCase(id);
    await refreshTestCases();
  };

  const startEdit = (tc: TestCase) => {
    setEditingId(tc.id);
    setEditForm({
      title: tc.title,
      preconditions: tc.preconditions,
      steps: tc.steps_json.join("\n"),
      expected_result: tc.expected_result,
      priority: tc.priority,
    });
  };

  const cancelEdit = () => setEditingId(null);

  const saveEdit = async (id: number) => {
    setSaving(true);
    try {
      await api.updateTestCase(id, {
        title: editForm.title,
        preconditions: editForm.preconditions,
        steps_json: editForm.steps.split("\n").map((s) => s.trim()).filter(Boolean),
        expected_result: editForm.expected_result,
        priority: editForm.priority,
      });
      setEditingId(null);
      await refreshTestCases();
    } catch (e) {
      setError(String(e));
    } finally {
      setSaving(false);
    }
  };

  const generateScript = async (tc: TestCase) => {
    setScriptStatus((s) => ({ ...s, [tc.id]: "Generating script..." }));
    try {
      const script = await api.generateScript(tc.id);
      setScripts((s) => ({ ...s, [tc.id]: script.code }));
      setScriptStatus((s) => ({ ...s, [tc.id]: "Script ready — click Download script" }));
    } catch (e) {
      setScriptStatus((s) => ({ ...s, [tc.id]: String(e) }));
    }
  };

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Test Cases</h2>
          <p className="page-subtitle">
            Search for a rule extracted from the latest uploaded workbook, then generate test cases for it.
          </p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-row">
          <input
            className="input"
            style={{ flex: 1 }}
            placeholder="Search rule name..."
            value={selectedRule ? selectedRule.rule_name : search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedRuleId(null);
            }}
          />
        </div>

        {search && !selectedRule && (
          <div className="table-scroll" style={{ marginTop: 8, maxHeight: 220 }}>
            {filteredRules.length === 0 ? (
              <div className="empty-state">No matching rules. Upload a workbook first.</div>
            ) : (
              <table className="data-table">
                <tbody>
                  {filteredRules.map((r) => (
                    <tr
                      key={r.id}
                      style={{ cursor: "pointer" }}
                      onClick={() => {
                        setSelectedRuleId(r.id);
                        setSearch("");
                      }}
                    >
                      <td>{r.rule_name}</td>
                      <td style={{ color: "var(--text-muted)" }}>{r.sheet_name}</td>
                      <td style={{ color: "var(--text-muted)" }}>{r.workflow}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {selectedRule && (
          <p className="status-note" style={{ marginTop: 8 }}>
            {selectedRule.description} ({selectedRule.sheet_name}
            {selectedRule.workflow ? ` · ${selectedRule.workflow}` : ""})
            <button
              className="btn btn-secondary btn-sm"
              style={{ marginLeft: 8 }}
              onClick={() => setSelectedRuleId(null)}
            >
              Change
            </button>
          </p>
        )}

        <div className="form-row" style={{ marginTop: 12 }}>
          <button className="btn btn-primary" onClick={generate} disabled={!selectedRuleId || generating}>
            {generating ? (
              <>
                <span className="spinner" /> Generating test cases...
              </>
            ) : (
              "Generate test cases for selected rule"
            )}
          </button>
        </div>
      </div>

      {testCases.length === 0 ? (
        <div className="empty-state">No test cases yet — pick a rule above, then generate.</div>
      ) : (
        testCases.map((tc) => (
          <div key={tc.id} className="test-case">
            <div className="test-case-header">
              <span className="test-case-title">{tc.title}</span>
              <span className="test-case-badges">
                <span className={`badge ${PRIORITY_BADGE[tc.priority] ?? "badge-neutral"}`}>{tc.priority}</span>
                <span className={`badge ${STATUS_BADGE[tc.status] ?? "badge-neutral"}`}>{tc.status}</span>
              </span>
            </div>

            {editingId === tc.id ? (
              <>
                <div className="form-row" style={{ marginTop: 8 }}>
                  <input
                    className="input"
                    style={{ flex: 1 }}
                    value={editForm.title}
                    onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))}
                    placeholder="Title"
                  />
                  <select
                    className="select"
                    style={{ maxWidth: 160 }}
                    value={editForm.priority}
                    onChange={(e) => setEditForm((f) => ({ ...f, priority: e.target.value }))}
                  >
                    <option value="critical">critical</option>
                    <option value="high">high</option>
                    <option value="medium">medium</option>
                    <option value="low">low</option>
                  </select>
                </div>
                <textarea
                  className="input"
                  style={{ width: "100%", marginTop: 8, minHeight: 48 }}
                  value={editForm.preconditions}
                  onChange={(e) => setEditForm((f) => ({ ...f, preconditions: e.target.value }))}
                  placeholder="Preconditions"
                />
                <textarea
                  className="input"
                  style={{ width: "100%", marginTop: 8, minHeight: 96 }}
                  value={editForm.steps}
                  onChange={(e) => setEditForm((f) => ({ ...f, steps: e.target.value }))}
                  placeholder="Steps (one per line)"
                />
                <textarea
                  className="input"
                  style={{ width: "100%", marginTop: 8, minHeight: 48 }}
                  value={editForm.expected_result}
                  onChange={(e) => setEditForm((f) => ({ ...f, expected_result: e.target.value }))}
                  placeholder="Expected result"
                />
                <div className="test-case-actions" style={{ marginTop: 8 }}>
                  <button className="btn btn-primary btn-sm" onClick={() => saveEdit(tc.id)} disabled={saving}>
                    {saving ? (
                      <>
                        <span className="spinner" /> Saving...
                      </>
                    ) : (
                      "Save"
                    )}
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={cancelEdit} disabled={saving}>
                    Cancel
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="test-case-meta">
                  <strong>Preconditions:</strong> {tc.preconditions}
                </p>
                <ol className="steps-list">
                  {tc.steps_json.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
                <p className="test-case-meta">
                  <strong>Expected:</strong> {tc.expected_result}
                </p>
                <p className="trace-note">Trace: {tc.requirement_trace}</p>

                <div className="test-case-actions">
                  {tc.status !== "approved" && (
                    <button className="btn btn-secondary btn-sm" onClick={() => startEdit(tc)}>
                      Edit
                    </button>
                  )}
                  {tc.status !== "approved" && (
                    <button className="btn btn-secondary btn-sm" onClick={() => approve(tc.id)}>
                      Approve
                    </button>
                  )}
                  {tc.status === "approved" && (
                    <button className="btn btn-secondary btn-sm" onClick={() => generateScript(tc)}>
                      {scripts[tc.id] ? "Regenerate Playwright script" : "Generate Playwright script"}
                    </button>
                  )}
                  {tc.status === "approved" && scripts[tc.id] && (
                    <button className="btn btn-secondary btn-sm" onClick={() => downloadScript(tc, scripts[tc.id])}>
                      Download script
                    </button>
                  )}
                  {scriptStatus[tc.id] && (
                    <span className="status-note">
                      {scriptStatus[tc.id] === "Generating script..." && <span className="spinner" />}
                      {scriptStatus[tc.id]}
                    </span>
                  )}
                </div>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}
