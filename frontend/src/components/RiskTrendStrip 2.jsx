const SEVERITY = { Low: 1, Medium: 2, High: 3, Critical: 4 }
const BASELINE = [64, 55, 46, 40, 38, 43, 47, 54]

export default function RiskTrendStrip({ runs = [] }) {
  const values = runs.length ? runs.slice(-8).map((run) => Math.max(10, (SEVERITY[run.severity] || 1) * (run.probability || .2) * 25)) : BASELINE
  const points = values.map((value, index) => `${index * (700 / Math.max(1, values.length - 1))},${100 - value}`).join(' ')
  return <section className="panel trend-panel"><div><span className="eyebrow">Live intelligence</span><h2>Global supply chain risk monitor</h2></div><span className="trend-caption">RISK INDEX · LAST 8 INTERVALS</span><div className="sparkline"><svg viewBox="0 0 700 110" preserveAspectRatio="none" aria-label="Risk trend"><defs><linearGradient id="riskLine" x1="0" x2="1"><stop stopColor="#55b9ff"/><stop offset=".55" stopColor="#da6678"/><stop offset="1" stopColor="#61dba2"/></linearGradient><linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#438ad0" stopOpacity=".18"/><stop offset="1" stopColor="#438ad0" stopOpacity="0"/></linearGradient></defs><polygon points={`0,110 ${points} 700,110`} fill="url(#riskFill)"/><polyline points={points} fill="none" stroke="url(#riskLine)" strokeWidth="2.2" vectorEffect="non-scaling-stroke"/>{values.map((value,index)=><circle key={index} cx={index*(700/Math.max(1,values.length-1))} cy={100-value} r="2.5" fill="#a9ddff"/>)}</svg><div className="chart-labels"><span>12:00</span><span>13:00</span><span>14:00</span><span>15:00</span><span>16:00</span></div></div></section>
}
