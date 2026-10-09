import { api, type Customer } from "../api/client";

export default function Reports({ customer }: { customer: Customer }) {
  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Audit Report</h2>
          <p className="page-subtitle">Traceability from requirement documents through test cases to run results.</p>
        </div>
        <a className="link" href={api.reportUrl(customer.id)} target="_blank" rel="noreferrer">
          Open in new tab ↗
        </a>
      </div>

      <iframe className="report-frame" src={api.reportUrl(customer.id)} title="Audit report" />
    </div>
  );
}
