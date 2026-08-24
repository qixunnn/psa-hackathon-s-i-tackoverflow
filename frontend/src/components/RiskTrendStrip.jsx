const SEVERITY = { Low: 1, Medium: 2, High: 3, Critical: 4 }

export default function RiskTrendStrip({ runs = [] }) {
  return <section className="panel trend-panel"><div><span className="eyebrow">Recent runs</span><h2>Risk pulse</h2></div><div className="sparkline">{runs.slice(-8).map((run) => { const score = run.severity ? (SEVERITY[run.severity] || 0) * (run.probability || 0) : 0; return <div className="bar" key={run.run_id} style={{ height: `${Math.max(8, score * 25)}%` }} title={`${run.run_id}: ${score.toFixed(2)}`} /> })}</div><span className="trend-caption">Severity × probability</span></section>
}
