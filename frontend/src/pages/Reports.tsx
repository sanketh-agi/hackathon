import { useEffect, useMemo, useState } from "react";
import { api, type Customer, type TestCase } from "../api/client";
import { BarChart, DonutChart, StatTile, type Slice } from "../components/Charts";

export default function Reports({ customer }: { customer: Customer }) {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .listTestCases(customer.id)
      .then((cases) => {
        if (!cancelled) setTestCases(cases);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [customer.id]);

  const stats = useMemo(() => {
    const total = testCases.length;
    const approved = testCases.filter((c) => c.status === "approved").length;
    const draft = total - approved;
    const approvalRate = total > 0 ? Math.round((approved / total) * 100) : 0;

    const priorityOrder = ["critical", "high", "medium", "low"];
    const priorityColor: Record<string, string> = {
      critical: "var(--chart-critical)",
      high: "var(--chart-high)",
      medium: "var(--chart-medium)",
      low: "var(--chart-low)",
    };
    const priority: Slice[] = priorityOrder
      .map((p) => ({
        label: p[0].toUpperCase() + p.slice(1),
        value: testCases.filter((c) => c.priority === p).length,
        color: priorityColor[p],
      }))
      .filter((s) => s.value > 0);

    const statusSlices: Slice[] = [
      { label: "Approved", value: approved, color: "var(--chart-pass)" },
      { label: "Draft", value: draft, color: "var(--chart-neutral)" },
    ];

    return { total, approved, draft, approvalRate, priority, statusSlices };
  }, [testCases]);

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Audit Report</h2>
          <p className="page-subtitle">Traceability from requirement documents through to generated test cases.</p>
        </div>
        <a className="link" href={api.reportUrl(customer.id)} target="_blank" rel="noreferrer">
          Open full report ↗
        </a>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="empty-state">
          <span className="spinner" /> Loading report…
        </div>
      ) : stats.total === 0 ? (
        <div className="empty-state">No test cases yet — generate some to see the report.</div>
      ) : (
        <>
          <div className="stat-grid">
            <StatTile label="Total test cases" value={stats.total} accent />
            <StatTile label="Approved" value={stats.approved} />
            <StatTile label="Draft" value={stats.draft} />
            <StatTile label="Approval rate" value={`${stats.approvalRate}%`} />
          </div>

          <div className="chart-grid">
            <div className="card chart-card">
              <h3 className="section-title" style={{ marginTop: 0 }}>Review status</h3>
              <DonutChart
                slices={stats.statusSlices}
                centerValue={`${stats.approved}/${stats.total}`}
                centerLabel="approved"
              />
            </div>

            <div className="card chart-card">
              <h3 className="section-title" style={{ marginTop: 0 }}>Test cases by priority</h3>
              {stats.priority.length === 0 ? (
                <p className="status-note">No priorities assigned yet.</p>
              ) : (
                <BarChart slices={stats.priority} />
              )}
            </div>
          </div>

          <h3 className="section-title">Full traceability report</h3>
          <iframe className="report-frame" src={api.reportUrl(customer.id)} title="Audit report" />
        </>
      )}
    </div>
  );
}
