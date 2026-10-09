/* Dependency-free, theme-aware inline-SVG charts.
   Marks read CSS custom properties, so they recolor with light/dark mode.
   Text uses ink tokens (never the data color); every mark carries a legend
   swatch or direct label so identity is never color-alone. */

export interface Slice {
  label: string;
  value: number;
  color: string; // a CSS var() reference, e.g. "var(--chart-pass)"
}

/* ---------- stat tile ---------- */

export function StatTile({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: number | string;
  accent?: boolean;
}) {
  return (
    <div className={`stat-tile${accent ? " stat-tile-accent" : ""}`}>
      <div className="stat-tile-value">{value}</div>
      <div className="stat-tile-label">{label}</div>
    </div>
  );
}

/* ---------- donut ---------- */

function polar(cx: number, cy: number, r: number, angle: number) {
  const a = (angle - 90) * (Math.PI / 180);
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function arcPath(cx: number, cy: number, r: number, start: number, end: number) {
  const s = polar(cx, cy, r, end);
  const e = polar(cx, cy, r, start);
  const large = end - start <= 180 ? 0 : 1;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 0 ${e.x} ${e.y}`;
}

export function DonutChart({
  slices,
  centerValue,
  centerLabel,
}: {
  slices: Slice[];
  centerValue: string;
  centerLabel: string;
}) {
  const total = slices.reduce((sum, s) => sum + s.value, 0);
  const size = 180;
  const cx = size / 2;
  const cy = size / 2;
  const r = 70;
  const stroke = 20;

  let cursor = 0;
  // 2px surface gap between segments → tiny angular gap
  const gapDeg = total > 0 && slices.filter((s) => s.value > 0).length > 1 ? 3 : 0;

  return (
    <div className="chart-donut">
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} role="img">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--chart-track)" strokeWidth={stroke} />
        {total > 0 &&
          slices
            .filter((s) => s.value > 0)
            .map((s) => {
              const frac = s.value / total;
              const start = cursor + gapDeg / 2;
              const end = cursor + frac * 360 - gapDeg / 2;
              cursor += frac * 360;
              return (
                <path
                  key={s.label}
                  d={arcPath(cx, cy, r, start, Math.max(start, end))}
                  fill="none"
                  stroke={s.color}
                  strokeWidth={stroke}
                  strokeLinecap="round"
                >
                  <title>{`${s.label}: ${s.value} (${Math.round(frac * 100)}%)`}</title>
                </path>
              );
            })}
        <text x={cx} y={cy - 4} textAnchor="middle" className="chart-donut-value">
          {centerValue}
        </text>
        <text x={cx} y={cy + 16} textAnchor="middle" className="chart-donut-label">
          {centerLabel}
        </text>
      </svg>
      <ul className="chart-legend">
        {slices.map((s) => (
          <li key={s.label}>
            <span className="chart-legend-dot" style={{ background: s.color }} />
            <span className="chart-legend-label">{s.label}</span>
            <span className="chart-legend-value">{s.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ---------- horizontal bars ---------- */

export function BarChart({ slices }: { slices: Slice[] }) {
  const max = Math.max(1, ...slices.map((s) => s.value));
  return (
    <div className="chart-bars">
      {slices.map((s) => (
        <div className="chart-bar-row" key={s.label}>
          <span className="chart-bar-label">{s.label}</span>
          <div className="chart-bar-track">
            <div
              className="chart-bar-fill"
              style={{ width: `${(s.value / max) * 100}%`, background: s.color }}
              title={`${s.label}: ${s.value}`}
            />
          </div>
          <span className="chart-bar-value">{s.value}</span>
        </div>
      ))}
    </div>
  );
}
