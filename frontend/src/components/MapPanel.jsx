import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { formatEta, formatEtaDelta, graphAffectedChokepoints, routeLayerStyle, routeName } from '../lib/routePresentation'

const ROUTE_COORDINATES = {
  'RT-001-BASELINE': [[4.48,51.92],[3.2,51.4],[1,50.9],[-5,48.5],[-9,44],[-10,37],[-5.6,36],[2,37],[12,35],[20,33],[29.9,31.2],[32.55,29.95],[34,25],[38,18],[43.3,12.6],[50,10],[60,5],[72,6],[85,6],[94.8,6.4],[99.65,5.55],[103.82,1.26]],
  'RT-002-CAPE-BYPASS': [[4.48,51.92],[3.2,51.4],[1,50.9],[-5,48.5],[-9,44],[-10,37],[-17,30],[-17,15],[-5,2],[8,-15],[18.5,-34.8],[30,-32],[45,-20],[60,-10],[75,-2],[90,5],[99.65,5.55],[103.82,1.26]],
}
const ROUTE_COLORS = {'RT-001-BASELINE':'#62c3b0','RT-002-CAPE-BYPASS':'#e3a45b'}
function routeFeature(route) {
  return { type:'Feature', properties:{ id:route.route_id }, geometry:{ type:'LineString', coordinates:ROUTE_COORDINATES[route.route_id] } }
}

function makeMarker(map, coordinates, label, kind='') {
  const marker = document.createElement('div')
  marker.className = `geo-marker ${kind}`
  marker.innerHTML = `<i></i><span>${label}</span>`
  return new maplibregl.Marker({ element:marker, anchor:'center' }).setLngLat(coordinates).addTo(map)
}

export default function MapPanel({ run, routes=[], vessel=null, selectedRoute=null, viewMode='2D' }) {
  const mapNode = useRef(null)
  const mapInstance = useRef(null)
  const affected = run?.risk_assessment?.affected_chokepoints || []
  const mappedAffected = graphAffectedChokepoints(affected, routes)
  const babRiskActive = mappedAffected.includes('Bab el-Mandeb')

  useEffect(() => {
    if (!mapNode.current || mapInstance.current) return undefined
    const displayRoutes = routes
    const map = new maplibregl.Map({ container:mapNode.current, style:'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', center:[46,9], zoom:2.25, minZoom:1.5, maxZoom:9, attributionControl:false })
    mapInstance.current = map
    map.addControl(new maplibregl.NavigationControl({ showCompass:false }), 'bottom-right')
    map.addControl(new maplibregl.AttributionControl({ compact:true }), 'bottom-left')
    map.on('load', () => {
      displayRoutes.filter(route => ROUTE_COORDINATES[route.route_id]).sort((a,b) => a.route_id === 'RT-001-BASELINE' ? 1 : b.route_id === 'RT-001-BASELINE' ? -1 : 0).forEach(route => {
        const id = route.route_id
        map.addSource(id, { type:'geojson', data:routeFeature(route) })
        map.addLayer({ id:`${id}-glow`, type:'line', source:id, paint:{ 'line-color':ROUTE_COLORS[id], 'line-width':8, 'line-opacity':0 } })
        map.addLayer({ id, type:'line', source:id, paint:{ 'line-color':ROUTE_COLORS[id], 'line-width':1.8, 'line-opacity':.25, 'line-dasharray':[1,0] } })
      })
      map.addSource('bab-risk', { type:'geojson', data:{ type:'Feature', properties:{}, geometry:{ type:'Polygon', coordinates:[[[42.4,11.5],[42.7,14.1],[44.7,14.1],[44.4,11.5],[42.4,11.5]]] } } })
      map.addLayer({ id:'bab-risk-fill', type:'fill', source:'bab-risk', paint:{ 'fill-color':'#d86662', 'fill-opacity':0, 'fill-outline-color':'#ef8a7f' } })
      makeMarker(map,[4.48,51.92],'ROTTERDAM','origin')
      makeMarker(map,[32.55,29.95],'SUEZ CANAL','chokepoint')
      makeMarker(map,[43.3,12.6],'BAB EL-MANDEB','risk')
      makeMarker(map,[18.5,-34.8],'CAPE OF GOOD HOPE','waypoint')
      makeMarker(map,[99.65,5.55],'STRAIT OF MALACCA','chokepoint')
      makeMarker(map,[103.82,1.26],'PSA SINGAPORE','destination')
      map.fitBounds([[-22,-40],[108,56]], { padding:{top:55,right:55,bottom:65,left:55}, duration:0 })
    })
    return () => { map.remove(); mapInstance.current=null }
  }, [routes])

  useEffect(() => {
    const map = mapInstance.current
    if (map?.isStyleLoaded()) map.easeTo({ pitch:viewMode==='3D'?45:0, bearing:viewMode==='3D'?-8:0, duration:700 })
  }, [viewMode])

  useEffect(() => {
    const map = mapInstance.current
    if (!map) return undefined
    const applyRunState = () => {
      if (map.getLayer('bab-risk-fill')) map.setPaintProperty('bab-risk-fill', 'fill-opacity', babRiskActive ? .26 : 0)
      Object.keys(ROUTE_COORDINATES).forEach((id) => {
        if (!map.getLayer(id)) return
        const style = routeLayerStyle(id, selectedRoute?.route_id, vessel?.scheduled_route_id)
        map.setPaintProperty(id, 'line-width', style.lineWidth)
        map.setPaintProperty(id, 'line-opacity', style.lineOpacity)
        map.setPaintProperty(id, 'line-dasharray', style.lineDasharray)
        if (map.getLayer(`${id}-glow`)) map.setPaintProperty(`${id}-glow`, 'line-opacity', style.glowOpacity)
      })
      if (selectedRoute?.route_id && map.getLayer(selectedRoute.route_id)) {
        map.moveLayer(`${selectedRoute.route_id}-glow`)
        map.moveLayer(selectedRoute.route_id)
      }
    }
    if (map.isStyleLoaded()) applyRunState()
    else map.once('load', applyRunState)
    return () => map.off('load', applyRunState)
  }, [babRiskActive, routes, run, selectedRoute?.route_id, vessel?.scheduled_route_id])

  return <section className={`world-map ${babRiskActive ? 'risk-active' : ''}`} aria-label="Geographic map of the Rotterdam to PSA Singapore corridor"><div ref={mapNode} className="maplibre-host"/><div className="map-vessel-card"><span>ACTIVE VESSEL</span><strong>{vessel?.vessel_name || 'Vessel pending'}</strong><dl><div><dt>{selectedRoute?.is_scheduled_fallback ? 'Scheduled route' : 'Selected route'}</dt><dd>{selectedRoute ? `${selectedRoute.route_id} · ${routeName(selectedRoute.route_id)}` : 'Pending'}</dd></div><div><dt>{selectedRoute?.is_scheduled_fallback ? 'Scheduled ETA' : 'Revised ETA'}</dt><dd>{formatEta(selectedRoute?.eta)}</dd></div><div><dt>ETA impact</dt><dd className={selectedRoute?.eta_delta_days > 0 ? 'delay' : ''}>{formatEtaDelta(selectedRoute?.eta_delta_days)}</dd></div></dl></div><div className={`map-live-state ${mappedAffected.length?'alert':''}`}><span/> {mappedAffected.length?`${mappedAffected.join(', ')} RISK ACTIVE`:'MONITORING MVP CORRIDOR'}</div></section>
}
