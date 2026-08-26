const ROUTE_NAMES = {
  'RT-001-BASELINE': 'Baseline route',
  'RT-002-CAPE-BYPASS': 'Cape bypass',
}

export function routeName(routeId) {
  return ROUTE_NAMES[routeId] || routeId || 'Route pending'
}

export function selectedRouteFromState(run, routes = [], vessel = null) {
  const rankedSelection = run?.ranked_routes?.find((route) => route.rank === 1)
  const routeId = rankedSelection?.route_id || vessel?.scheduled_route_id
  if (!routeId) return null

  const graphRoute = routes.find((route) => route.route_id === routeId) || {}
  return {
    ...graphRoute,
    ...(rankedSelection || {}),
    route_id: routeId,
    eta: rankedSelection?.eta || vessel?.scheduled_arrival || null,
    eta_delta_days: rankedSelection?.eta_delta_days ?? 0,
    is_scheduled_fallback: !rankedSelection,
  }
}

export function operationalRoutesFromState(routes = [], vessel = null, run = null) {
  if (!vessel?.scheduled_route_id) return []
  const visibleRouteIds = new Set([vessel.scheduled_route_id])
  for (const candidate of run?.candidate_routes || []) {
    visibleRouteIds.add(candidate.route_id)
  }
  return routes.filter((route) => visibleRouteIds.has(route.route_id))
}

export function riskScenarioFromState(run) {
  const assessment = run?.risk_assessment
  if (!assessment) {
    return {
      active: false,
      title: 'Awaiting intelligence assessment',
      severity: 'IDLE',
      chokepoint: '—',
      probability: '—',
      duration: '—',
    }
  }
  const chokepoint = assessment.affected_chokepoints?.[0] || null
  return {
    active: true,
    title: `${chokepoint || 'Maritime'} disruption`,
    severity: assessment.severity,
    chokepoint: chokepoint || '—',
    probability: `${Math.round(assessment.probability * 100)}%`,
    duration: assessment.estimated_duration || '—',
  }
}

export function formatEta(eta) {
  if (!eta) return 'Pending'
  const parsed = new Date(eta)
  if (Number.isNaN(parsed.getTime())) return 'Pending'
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${String(parsed.getUTCDate()).padStart(2, '0')} ${months[parsed.getUTCMonth()]} ${parsed.getUTCFullYear()}`
}

export function formatEtaDelta(days) {
  if (!Number.isFinite(days)) return 'ETA impact pending'
  const sign = days > 0 ? '+' : ''
  return `${sign}${days} ${Math.abs(days) === 1 ? 'day' : 'days'}`
}

export function routeLayerStyle(routeId, selectedRouteId, scheduledRouteId) {
  const isSelected = routeId === selectedRouteId
  const isMutedBaseline = routeId === scheduledRouteId && !isSelected
  return {
    lineWidth: isSelected ? 5 : isMutedBaseline ? 2.4 : 1.6,
    lineOpacity: isSelected ? 1 : isMutedBaseline ? 0.38 : 0.2,
    lineDasharray: isSelected ? [1, 0] : isMutedBaseline ? [2, 2] : [1, 0],
    glowOpacity: isSelected ? 0.28 : 0,
  }
}

export function graphAffectedChokepoints(affected = [], routes = []) {
  const represented = new Set(routes.flatMap((route) => route.chokepoints || []))
  return affected.filter((chokepoint) => represented.has(chokepoint))
}
