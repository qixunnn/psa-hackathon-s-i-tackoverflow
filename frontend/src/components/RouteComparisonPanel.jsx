export default function RouteComparisonPanel({ run, routes = [] }) {
  const routeMap = new Map(routes.map((route) => [route.route_id, route]))
  const rankedById = new Map((run?.ranked_routes || []).map((route) => [route.route_id, route]))
  const routeIds = (run?.candidate_routes || []).map((candidate) => candidate.route_id)
  for (const ranked of run?.ranked_routes || []) {
    if (!routeIds.includes(ranked.route_id)) routeIds.push(ranked.route_id)
  }
  const rows = routeIds.map((routeId) => ({
    ...routeMap.get(routeId),
    ...rankedById.get(routeId),
    route_id: routeId,
  })).sort((a, b) => (a.rank || Number.MAX_SAFE_INTEGER) - (b.rank || Number.MAX_SAFE_INTEGER))
  const hasRankings = rankedById.size > 0

  return <section className="panel route-panel"><div className="section-heading"><div><span className="eyebrow">Current assessment</span><h2>Route comparison</h2></div><span className="count-badge">{rows.length} {hasRankings ? 'ranked' : 'candidates'}</span></div>{rows.length === 0 ? <p className="empty-state">Route candidates will appear after Agent 3 completes.</p> : <div className="table-wrap"><table><thead><tr><th>Route</th><th>Distance (nm)</th><th>Transit Days</th><th>ETA</th><th>Δ vs scheduled</th><th>Chokepoints</th></tr></thead><tbody>{rows.map((row) => {
    const isRanked = Number.isInteger(row.rank)
    return <tr className={row.rank === 1 ? 'top-route' : ''} key={row.route_id}><td><b>{isRanked ? `#${row.rank}` : 'Candidate'} {row.route_id}</b></td><td>{row.distance_nm?.toLocaleString() || '—'}</td><td>{row.base_transit_days ?? '—'}</td><td>{isRanked ? new Date(row.eta).toLocaleDateString() : 'Pending Agent 4'}</td><td className={row.eta_delta_days > 0 ? 'delay' : ''}>{isRanked ? `${row.eta_delta_days > 0 ? '+' : ''}${row.eta_delta_days}d` : '—'}</td><td>{row.chokepoints?.join(', ') || '—'}</td></tr>
  })}</tbody></table></div>}</section>
}
