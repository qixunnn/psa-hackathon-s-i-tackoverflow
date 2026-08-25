export default function RouteGraphViewer({ routes = [], vessel, affectedChokepoints = [] }) {
  const affected = new Set(affectedChokepoints)
  return <section className="workspace-view">
    <div className="workspace-head">
      <div><span className="eyebrow">Read-only · admin</span><h2>Route graph viewer</h2></div>
      <span className="count-badge">{routes.length} routes</span>
    </div>
    <p className="workspace-note">
      These are the only paths the Route Retrieval Agent may select from — it performs graph
      lookups, never route invention. The graph is fixed for the MVP and is not editable here.
    </p>
    {routes.length === 0
      ? <p className="empty-state">Route graph unavailable. Confirm the backend is running.</p>
      : <div className="graph-grid">
          {routes.map((route) => {
            const isBaseline = vessel?.scheduled_route_id === route.route_id
            const exposed = route.chokepoints.filter((chokepoint) => affected.has(chokepoint))
            return <article className={`graph-card ${isBaseline ? 'baseline' : ''}`} key={route.route_id}>
              <div className="graph-card-head">
                <strong>{route.route_id}</strong>
                {isBaseline && <span className="tag ok">Scheduled baseline</span>}
                {exposed.length > 0 && <span className="tag bad">Exposed</span>}
              </div>
              <p className="graph-corridor">{route.origin} → {route.destination}</p>
              <dl className="graph-stats">
                <div><dt>Distance</dt><dd>{route.distance_nm.toLocaleString()} nm</dd></div>
                <div><dt>Base transit</dt><dd>{route.base_transit_days} days</dd></div>
                <div><dt>Chokepoints</dt><dd>{route.chokepoints.length}</dd></div>
              </dl>
              <ol className="waypoint-chain">
                {route.waypoints.map((waypoint) => <li
                  key={waypoint}
                  className={route.chokepoints.includes(waypoint) ? (affected.has(waypoint) ? 'chokepoint affected' : 'chokepoint') : ''}
                >{waypoint}</li>)}
              </ol>
            </article>
          })}
        </div>}
    {vessel && <p className="workspace-note">
      MVP vessel <b>{vessel.vessel_name}</b> · scheduled arrival{' '}
      <b>{new Date(vessel.scheduled_arrival).toLocaleDateString()}</b> on <b>{vessel.scheduled_route_id}</b>.
    </p>}
  </section>
}
