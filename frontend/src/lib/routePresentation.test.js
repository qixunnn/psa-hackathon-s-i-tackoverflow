import { describe, expect, it } from 'vitest'
import {
  formatEta,
  formatEtaDelta,
  graphAffectedChokepoints,
  routeLayerStyle,
  selectedRouteFromState,
} from './routePresentation'

const routes = [
  { route_id: 'RT-001-BASELINE', distance_nm: 3900, chokepoints: ['Strait of Hormuz', 'Strait of Malacca'] },
  { route_id: 'RT-002-FUJAIRAH-BYPASS', distance_nm: 4100, chokepoints: ['Strait of Malacca'] },
  { route_id: 'RT-003-ESCORTED-TRANSIT', distance_nm: 3900, chokepoints: ['Strait of Hormuz', 'Strait of Malacca'] },
]
const vessel = {
  vessel_name: 'MV Pacific Voyager',
  scheduled_route_id: 'RT-001-BASELINE',
  scheduled_arrival: '2026-09-04T16:26:26Z',
}

describe('route presentation', () => {
  it('uses the rank-1 pipeline route instead of candidate order or scheduled baseline', () => {
    const run = {
      candidate_routes: [
        { route_id: 'RT-001-BASELINE' },
        { route_id: 'RT-002-FUJAIRAH-BYPASS' },
      ],
      ranked_routes: [
        { route_id: 'RT-001-BASELINE', rank: 2, eta: '2026-09-04T16:26:26Z', eta_delta_days: 0 },
        { route_id: 'RT-002-FUJAIRAH-BYPASS', rank: 1, eta: '2026-09-06T16:26:26Z', eta_delta_days: 2 },
      ],
    }

    expect(selectedRouteFromState(run, routes, vessel)).toMatchObject({
      route_id: 'RT-002-FUJAIRAH-BYPASS',
      distance_nm: 4100,
      eta: '2026-09-06T16:26:26Z',
      eta_delta_days: 2,
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

  it('makes the selected bypass prominent and the baseline muted and dashed', () => {
    expect(routeLayerStyle('RT-002-FUJAIRAH-BYPASS', 'RT-002-FUJAIRAH-BYPASS', 'RT-001-BASELINE')).toEqual({
      lineWidth: 5,
      lineOpacity: 1,
      lineDasharray: [1, 0],
      glowOpacity: 0.28,
    })
    expect(routeLayerStyle('RT-001-BASELINE', 'RT-002-FUJAIRAH-BYPASS', 'RT-001-BASELINE')).toMatchObject({
      lineOpacity: 0.38,
      lineDasharray: [2, 2],
      glowOpacity: 0,
    })
  })

  it('does not present Bab el-Mandeb as active on the Jebel Ali route graph', () => {
    expect(graphAffectedChokepoints(['Bab el-Mandeb', 'Strait of Hormuz'], routes)).toEqual(['Strait of Hormuz'])
  })

  it('formats the selected route ETA impact for the vessel card and legend', () => {
    expect(formatEta('2026-09-06T16:26:26Z')).toBe('06 Sep 2026')
    expect(formatEtaDelta(2)).toBe('+2 days')
  })
})
