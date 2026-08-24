const WAYPOINTS = [
  ['Jebel Ali', 62, 154], ['Strait of Hormuz', 190, 96], ['Arabian Sea', 330, 148], ['Strait of Malacca', 500, 88], ['PSA Singapore', 654, 136],
]

export default function MapPanel({ run }) {
  const affected = run?.risk_assessment?.affected_chokepoints || []
  return <section className="panel map-panel"><div className="section-heading"><div><span className="eyebrow">Live corridor</span><h2>Jebel Ali → PSA Singapore</h2></div><span className="map-status">{affected.length ? 'Risk overlay active' : 'Monitoring'}</span></div><svg viewBox="0 0 720 220" role="img" aria-label="Schematic shipping route from Jebel Ali to PSA Singapore"><path className="route-shadow" d="M62 154 Q125 70 190 96 T330 148 T500 88 T654 136" /><path className="route-line" d="M62 154 Q125 70 190 96 T330 148 T500 88 T654 136" />{WAYPOINTS.map(([name, x, y]) => { const highlighted = affected.includes(name); return <g key={name} className={highlighted ? 'waypoint highlighted' : 'waypoint'}><circle cx={x} cy={y} r={highlighted ? 10 : 6} /><text x={x} y={y + 25}>{name}</text></g> })}</svg></section>
}
