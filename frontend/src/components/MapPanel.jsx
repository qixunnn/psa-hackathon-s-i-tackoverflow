import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { formatEta, formatEtaDelta, graphAffectedChokepoints, routeLayerStyle, routeName } from '../lib/routePresentation'

const ROUTE_COORDINATES = {
  'RT-001-BASELINE': [[55.03,24.99],[55.35,25.18],[56.25,26.55],[57.1,24.4],[61.5,20.2],[66.5,14.2],[72.5,9.2],[79.8,6.1],[87.2,5.5],[94.8,6.4],[99.65,5.55],[101.3,3.15],[103.82,1.26]],
  'RT-002-FUJAIRAH-BYPASS': [[55.03,24.99],[56.34,25.12],[58,23.4],[61.5,20.2],[66.5,14.2],[72.5,9.2],[79.8,6.1],[87.2,5.5],[94.8,6.4],[99.65,5.55],[101.3,3.15],[103.82,1.26]],
  'RT-003-ESCORTED-TRANSIT': [[55.03,24.99],[55.35,25.18],[56.25,26.55],[57.1,24.4],[61.5,20.2],[66.5,14.2],[72.5,9.2],[79.8,6.1],[87.2,5.5],[94.8,6.4],[99.65,5.55],[101.3,3.15],[103.82,1.26]],
}
const ROUTE_COLORS = {'RT-001-BASELINE':'#62c3b0','RT-002-FUJAIRAH-BYPASS':'#e3a45b','RT-003-ESCORTED-TRANSIT':'#91a0ae'}
const FALLBACK_ROUTES = Object.keys(ROUTE_COORDINATES).map((route_id) => ({ route_id }))

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
  const hormuzRiskActive = mappedAffected.includes('Strait of Hormuz')

  useEffect(() => {
    if (!mapNode.current || mapInstance.current) return undefined
    const displayRoutes = routes.length ? routes : FALLBACK_ROUTES
    const map = new maplibregl.Map({ container:mapNode.current, style:'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', center:[78,13], zoom:3.25, minZoom:2, maxZoom:9, attributionControl:false })
    mapInstance.current = map
    map.addControl(new maplibregl.NavigationControl({ showCompass:false }), 'bottom-right')
    map.addControl(new maplibregl.AttributionControl({ compact:true }), 'bottom-left')
    map.on('load', () => {
      displayRoutes.filter(route => ROUTE_COORDINATES[route.route_id]).sort((a,b) => a.route_id === 'RT-001-BASELINE' ? 1 : b.route_id === 'RT-001-BASELINE' ? -1 : 0).forEach(route => {
        const id = route.route_id
        map.addSource(id, { type:'geojson', data:routeFeature(route) })
        map.addLayer({ id:`${id}-glow`, type:'line', source:id, paint:{ 'line-color':ROUTE_COLORS[id], 'line-width':8, 'line-opacity':0 } })
        map.addLayer({ id, type:'line', source:id, paint:{ 'line-color':ROUTE_COLORS[id], 'line-width':1.8, 'line-opacity':.25, 'line-dasharray':id==='RT-003-ESCORTED-TRANSIT'?[2,2]:[1,0] } })
      })
      map.addSource('hormuz-risk', { type:'geojson', data:{ type:'Feature', properties:{}, geometry:{ type:'Polygon', coordinates:[[[55.45,25.65],[56,27.15],[57,27.05],[57.2,25.65],[56.25,25.15],[55.45,25.65]]] } } })
      map.addLayer({ id:'hormuz-risk-fill', type:'fill', source:'hormuz-risk', paint:{ 'fill-color':'#d86662', 'fill-opacity':0, 'fill-outline-color':'#ef8a7f' } })
      makeMarker(map,[55.03,24.99],'JEBEL ALI','origin')
      makeMarker(map,[56.25,26.55],'STRAIT OF HORMUZ','risk')
      makeMarker(map,[99.65,5.55],'STRAIT OF MALACCA','chokepoint')
      makeMarker(map,[103.82,1.26],'PSA SINGAPORE','destination')
      map.fitBounds([[52,-1],[107,29]], { padding:{top:55,right:55,bottom:65,left:55}, duration:0 })
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
      if (map.getLayer('hormuz-risk-fill')) map.setPaintProperty('hormuz-risk-fill', 'fill-opacity', hormuzRiskActive ? .26 : 0)
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
  }, [hormuzRiskActive, routes, run, selectedRoute?.route_id, vessel?.scheduled_route_id])

  return <section className={`world-map ${hormuzRiskActive ? 'risk-active' : ''}`} aria-label="Geographic map of the Jebel Ali to PSA Singapore corridor"><div ref={mapNode} className="maplibre-host"/><div className="map-vessel-card"><span>ACTIVE VESSEL</span><strong>{vessel?.vessel_name || 'Vessel pending'}</strong><dl><div><dt>Selected route</dt><dd>{selectedRoute ? `${selectedRoute.route_id} · ${routeName(selectedRoute.route_id)}` : 'Pending'}</dd></div><div><dt>Revised ETA</dt><dd>{formatEta(selectedRoute?.eta)}</dd></div><div><dt>ETA impact</dt><dd className={selectedRoute?.eta_delta_days > 0 ? 'delay' : ''}>{formatEtaDelta(selectedRoute?.eta_delta_days)}</dd></div></dl></div><div className={`map-live-state ${mappedAffected.length?'alert':''}`}><span/> {mappedAffected.length?`${mappedAffected.join(', ')} RISK ACTIVE`:'MONITORING MVP CORRIDOR'}</div></section>
}
