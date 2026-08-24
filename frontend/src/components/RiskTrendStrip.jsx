const SEVERITY = { Low: 1, Medium: 2, High: 3, Critical: 4 }
const EMPTY_TREND = [5, 5, 5, 5, 5, 5, 5, 5]

export default function RiskTrendStrip({ runs = [], activeRun }) {
  const scoredRuns = runs.filter((run) => run.severity && run.probability)
  const risk = activeRun?.risk_assessment
  const values = scoredRuns.length
    ? scoredRuns.slice(-8).map((run) => Math.max(5, (SEVERITY[run.severity] || 0) * run.probability * 25))
    : risk ? [5, Math.max(5, SEVERITY[risk.severity] * risk.probability * 25)] : EMPTY_TREND
  const points = values.map((value, index) => `${index * (700 / Math.max(1, values.length - 1))},${100 - value}`).join(' ')
  return <section className="panel trend-panel"><div><span className="eyebrow">Recent runs</span><h2>MVP corridor risk trend</h2></div><span className="trend-caption">{risk ? `${risk.severity.toUpperCase()} · ${Math.round(risk.probability * 100)}% PROBABILITY` : 'AWAITING RISK-SCORED RUN'}</span><div className="sparkline"><svg viewBox="0 0 700 110" preserveAspectRatio="none" aria-label="Risk trend"><defs><linearGradient id="riskLine" x1="0" x2="1"><stop stopColor="#62c3b0"/><stop offset=".55" stopColor="#e3a45b"/><stop offset="1" stopColor="#d86662"/></linearGradient><linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#62c3b0" stopOpacity=".16"/><stop offset="1" stopColor="#62c3b0" stopOpacity="0"/></linearGradient></defs><polygon points={`0,110 ${points} 700,110`} fill="url(#riskFill)"/><polyline points={points} fill="none" stroke="url(#riskLine)" strokeWidth="2.2" vectorEffect="non-scaling-stroke"/>{values.map((value,index)=><circle key={index} cx={index*(700/Math.max(1,values.length-1))} cy={100-value} r="2.5" fill="#f0c98f"/>)}</svg><div className="chart-labels"><span>Oldest</span><span>Current</span></div></div></section>
}
