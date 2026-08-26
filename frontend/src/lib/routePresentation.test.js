import { describe, expect, it } from 'vitest'
import {
  formatEta,
  formatEtaDelta,
  graphAffectedChokepoints,
  operationalRoutesFromState,
  riskScenarioFromState,
  routeLayerStyle,
  selectedRouteFromState,
} from './routePresentation'

const routes = [
  { route_id: 'RT-001-BASELINE', distance_nm: 8300, chokepoints: ['Suez Canal', 'Bab el-Mandeb', 'Strait of Malacca'] },
  { route_id: 'RT-002-CAPE-BYPASS', distance_nm: 11700, chokepoints: ['Strait of Malacca'] },
]
const vessel = {
  vessel_name: 'MV Pacific Voyager',
  scheduled_route_id: 'RT-001-BASELINE',
  scheduled_arrival: '2026-09-20T16:26:26Z',
}

describe('route presentation', () => {
  it('uses the rank-1 pipeline route instead of candidate order or scheduled baseline', () => {
    const run = {
      candidate_routes: [
        { route_id: 'RT-001-BASELINE' },
        { route_id: 'RT-002-CAPE-BYPASS' },
      ],
      ranked_routes: [
        { route_id: 'RT-001-BASELINE', rank: 2, eta: '2026-09-04T16:26:26Z', eta_delta_days: 0 },
        { route_id: 'RT-002-CAPE-BYPASS', rank: 1, eta: '2026-09-30T16:26:26Z', eta_delta_days: 10 },
      ],
    }

    expect(selectedRouteFromState(run, routes, vessel)).toMatchObject({
      route_id: 'RT-002-CAPE-BYPASS',
      distance_nm: 11700,
      eta: '2026-09-30T16:26:26Z',
      eta_delta_days: 10,
      is_scheduled_fallback: false,
    })
  })

  it('uses the vessel scheduled route only while no ranked selection exists', () => {
    expect(selectedRouteFromState(null, routes, vessel)).toMatchObject({
      route_id: 'RT-001-BASELINE',
      eta_delta_days: 0,
      is_scheduled_fallback: true,
    })
  })

  it('shows only the scheduled baseline until Agent 3 returns candidates', () => {
    expect(operationalRoutesFromState(routes, vessel, null).map((route) => route.route_id)).toEqual([
      'RT-001-BASELINE',
    ])
    expect(operationalRoutesFromState(routes, vessel, {
      candidate_routes: [{ route_id: 'RT-001-BASELINE' }, { route_id: 'RT-002-CAPE-BYPASS' }],
    }).map((route) => route.route_id)).toEqual([
      'RT-001-BASELINE',
      'RT-002-CAPE-BYPASS',
    ])
  })

  it('keeps risk presentation neutral until Agent 2 output exists', () => {
    expect(riskScenarioFromState(null)).toEqual({
      active: false,
      title: 'Awaiting intelligence assessment',
      severity: 'IDLE',
      chokepoint: '—',
      probability: '—',
      duration: '—',
    })
    expect(riskScenarioFromState({ risk_assessment: {
      affected_chokepoints: ['Bab el-Mandeb'],
      severity: 'High',
      probability: 0.72,
      estimated_duration: '3-5 days',
    } })).toMatchObject({
      active: true,
      title: 'Bab el-Mandeb disruption',
      probability: '72%',
    })
  })

  it('makes the selected Cape bypass prominent and the baseline muted and dashed', () => {
    expect(routeLayerStyle('RT-002-CAPE-BYPASS', 'RT-002-CAPE-BYPASS', 'RT-001-BASELINE')).toEqual({
      lineWidth: 5,
      lineOpacity: 1,
      lineDasharray: [1, 0],
      glowOpacity: 0.28,
    })
    expect(routeLayerStyle('RT-001-BASELINE', 'RT-002-CAPE-BYPASS', 'RT-001-BASELINE')).toMatchObject({
      lineOpacity: 0.38,
      lineDasharray: [2, 2],
      glowOpacity: 0,
    })
  })

  it('presents Bab el-Mandeb but not unrelated Hormuz risk on the Rotterdam graph', () => {
    expect(graphAffectedChokepoints(['Bab el-Mandeb', 'Strait of Hormuz'], routes)).toEqual(['Bab el-Mandeb'])
  })

  it('formats the selected route ETA impact for the vessel card and legend', () => {
    expect(formatEta('2026-09-30T16:26:26Z')).toBe('30 Sep 2026')
    expect(formatEtaDelta(10)).toBe('+10 days')
  })
})
