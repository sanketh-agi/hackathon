from datetime import datetime, timezone
from html import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import models
from app.db import get_db

router = APIRouter(tags=["reports"])

PRIORITY_BADGE = {
    "critical": "badge-danger",
    "high": "badge-warning",
    "medium": "badge-info",
    "low": "badge-neutral",
}
STATUS_BADGE = {"approved": "badge-success", "draft": "badge-neutral"}
RUN_BADGE = {"passed": "badge-success", "failed": "badge-danger", "not run": "badge-neutral"}


def _badge(label: str, mapping: dict[str, str]) -> str:
    css_class = mapping.get(label, "badge-neutral")
    return f'<span class="badge {css_class}">{escape(label)}</span>'


def _stat(label: str, value: int) -> str:
    return f"""
    <div class="stat">
      <div class="stat-value">{value}</div>
      <div class="stat-label">{escape(label)}</div>
    </div>
    """


@router.get("/customers/{customer_id}/report", response_class=HTMLResponse)
def audit_report(customer_id: int, db: Session = Depends(get_db)):
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")

    test_cases = (
        db.query(models.TestCase)
        .filter(models.TestCase.customer_id == customer_id)
        .order_by(models.TestCase.id)
        .all()
    )

    approved_count = sum(1 for tc in test_cases if tc.status == "approved")
    passed_count = sum(1 for tc in test_cases if tc.runs and tc.runs[0].status == "passed")
    failed_count = sum(1 for tc in test_cases if tc.runs and tc.runs[0].status == "failed")

    rows = []
    for tc in test_cases:
        latest_run = tc.runs[0] if tc.runs else None
        run_status = latest_run.status if latest_run else "not run"
        rows.append(
            f"""
            <tr>
              <td>{tc.id}</td>
              <td><strong>{escape(tc.title)}</strong></td>
              <td>{_badge(tc.priority, PRIORITY_BADGE)}</td>
              <td>{_badge(tc.status, STATUS_BADGE)}</td>
              <td class="muted">{escape(tc.requirement_trace)}</td>
              <td>{_badge(run_status, RUN_BADGE)}</td>
            </tr>
            """
        )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Audit Report — {escape(customer.name)}</title>
      <style>
        :root {{
          --bg: #f5f6f8; --surface: #ffffff; --border: #e3e6ea; --text: #16181d;
          --text-muted: #6b7280; --primary: #4338ca;
          --success: #067647; --success-bg: #e7f6ee;
          --warning: #b45309; --warning-bg: #fef3e2;
          --danger: #b42318; --danger-bg: #fdeceb;
          --info: #175cd3; --info-bg: #eaf2fe;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          margin: 0; padding: 2rem; background: var(--bg); color: var(--text); font-size: 14px;
        }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }}
        h1 {{ margin: 0 0 0.25rem; font-size: 1.4rem; letter-spacing: -0.01em; }}
        .subtitle {{ color: var(--text-muted); font-size: 0.9rem; }}
        .generated {{ color: var(--text-muted); font-size: 0.8rem; text-align: right; }}
        .stats {{ display: flex; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }}
        .stat {{
          background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
          padding: 0.85rem 1.25rem; min-width: 120px; box-shadow: 0 1px 2px rgba(16,24,40,0.06);
        }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; }}
        .stat-label {{ color: var(--text-muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; margin-top: 0.15rem; }}
        table {{ border-collapse: collapse; width: 100%; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
        th, td {{ padding: 0.65rem 0.9rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
        th {{ background: var(--bg); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }}
        tr:last-child td {{ border-bottom: none; }}
        .muted {{ color: var(--text-muted); }}
        .badge {{
          display: inline-flex; align-items: center; padding: 0.15rem 0.55rem; border-radius: 999px;
          font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; white-space: nowrap;
        }}
        .badge-neutral {{ background: var(--bg); color: var(--text-muted); }}
        .badge-success {{ background: var(--success-bg); color: var(--success); }}
        .badge-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .badge-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .badge-info {{ background: var(--info-bg); color: var(--info); }}
        .empty {{ text-align: center; padding: 2rem; color: var(--text-muted); }}
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <h1>Audit Report — {escape(customer.name)}</h1>
          <div class="subtitle">Application URL: {escape(customer.app_url) or "—"}</div>
        </div>
        <div class="generated">Generated {generated_at}</div>
      </div>

      <div class="stats">
        {_stat("Total test cases", len(test_cases))}
        {_stat("Approved", approved_count)}
        {_stat("Passed (latest run)", passed_count)}
        {_stat("Failed (latest run)", failed_count)}
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th><th>Test Case</th><th>Priority</th><th>Status</th>
            <th>Requirement Trace</th><th>Last Run</th>
          </tr>
        </thead>
        <tbody>
          {"".join(rows) if rows else '<tr><td colspan="6" class="empty">No test cases yet</td></tr>'}
        </tbody>
      </table>
    </body>
    </html>
    """
    return HTMLResponse(html)
