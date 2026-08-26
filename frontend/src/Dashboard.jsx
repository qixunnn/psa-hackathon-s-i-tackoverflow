import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, ChevronDown, Globe2, History, Home, Layers3, Map, Radio, RefreshCw, ShieldCheck, Waypoints, X,
} from 'lucide-react'
import UrlSubmitForm from './components/UrlSubmitForm'
import AgentPipelineRail from './components/AgentPipelineRail'
import EventLog from './components/EventLog'
import AdvisoryCard from './components/AdvisoryCard'
import HistoryPanel from './components/HistoryPanel'
import MapPanel from './components/MapPanel'
import RiskTrendStrip from './components/RiskTrendStrip'
import RouteComparisonPanel from './components/RouteComparisonPanel'
import RouteGraphViewer from './components/RouteGraphViewer'
import { getRoutes, getVessel, listRuns } from './lib/api'
import { formatEtaDelta, operationalRoutesFromState, riskScenarioFromState, routeName, selectedRouteFromState } from './lib/routePresentation'
import { useRunStream } from './lib/useRunStream'

const NAV = [
  { id: 'home', label: 'Home', Icon: Home },
  { id: 'history', label: 'History', Icon: History },
  { id: 'routes', label: 'Route graph', Icon: Waypoints },
]

export default function Dashboard() {
  const [runId, setRunId] = useState(null)
  const [routes, setRoutes] = useState([])
  const [vessel, setVessel] = useState(null)
  const [recentRuns, setRecentRuns] = useState([])
  const [viewMode, setViewMode] = useState('2D')
  const [view, setView] = useState('home')
  const [assessmentStarting, setAssessmentStarting] = useState(false)
  const { status, run, events, isLoading } = useRunStream(runId)
  const selectedRoute = selectedRouteFromState(run, routes, vessel)
  const operationalRoutes = useMemo(
    () => operationalRoutesFromState(routes, vessel, run),
    [routes, vessel, run?.candidate_routes],
  )
  const riskScenario = riskScenarioFromState(run)
  const pipelineLabel = assessmentStarting ? 'RUNNING' : !runId ? 'READY' : status === 'complete' ? 'COMPLETE' : status === 'halted_not_relevant' ? 'NO IMPACT' : status === 'error' ? 'ERROR' : 'RUNNING'
  const runActive = assessmentStarting || Boolean(runId && !['complete', 'halted_not_relevant', 'error'].includes(status))
  const pipelineRun = assessmentStarting && (!run || run.status === 'queued')
    ? { ...run, status: 'extracting' }
    : run

  const refreshRuns = useCallback(() => { listRuns().then(setRecentRuns).catch(() => {}) }, [])

  useEffect(() => {
    getRoutes().then(setRoutes).catch(() => {})
    refreshRuns()
  }, [status, refreshRuns])

  useEffect(() => { getVessel().then(setVessel).catch(() => {}) }, [])

  useEffect(() => {
    if (run && run.status !== 'queued') setAssessmentStarting(false)
  }, [run])

  function openRun(nextRunId) {
    setRunId(nextRunId)
    setView('home')
  }

  function beginNewScan() {
    if (runActive) return
    setRunId(null)
    setView('home')
    requestAnimationFrame(() => document.querySelector('[aria-label="Article URL"]')?.focus())
  }

  function startAssessment() {
    setRunId(null)
    setAssessmentStarting(true)
    setView('home')
  }

  function assessmentCreated(nextRunId) {
    setRunId(nextRunId)
  }

  function assessmentStartFailed() {
    setAssessmentStarting(false)
  }

  return <main className="command-shell">
    <header className="command-header">
      <div className="header-left">
        <div className="shield-logo"><ShieldCheck size={20} /></div>
        <nav className="primary-nav" aria-label="Primary navigation">
          {NAV.map(({ id, label, Icon }) => <button
            key={id}
            className={`nav-button ${view === id ? 'active' : ''}`}
            aria-current={view === id ? 'page' : undefined}
            onClick={() => setView(id)}
          ><Icon size={15} /> {label}</button>)}
        </nav>
        <div className="product-title"><strong>PSA Sentinel</strong><span>Agentic supply-chain risk advisory</span></div>
      </div>
      <div className="header-actions">
        <button className="control-button quiet"><Radio size={14} /> Pipeline live</button>
        <button className="control-button" onClick={beginNewScan} disabled={runActive}><RefreshCw size={14} /> New scan</button>
        <div className="view-switch">
          {['2D', '3D'].map((mode) => <button key={mode} className={viewMode === mode ? 'selected' : ''} onClick={() => setViewMode(mode)}>{mode === '2D' ? <Map size={14} /> : <Globe2 size={14} />}{mode}</button>)}
        </div>
        <span className={`system-pill ${routes.length ? '' : 'offline'}`}><i /> {routes.length ? 'API connected' : 'API unavailable'}</span>
      </div>
    </header>

    <div className="command-layout">
      <section className="operations-canvas">
        <MapPanel run={run} routes={operationalRoutes} vessel={vessel} selectedRoute={selectedRoute} viewMode={viewMode} />
        <aside className="map-controls floating-panel">
          <div className="floating-title"><span><Layers3 size={15} /> Map controls</span><ChevronDown size={14} /></div>
          <div className="control-content">
            <div className="control-card-heading"><strong>MVP corridor</strong><span>LIVE</span></div>
            <dl className="map-stat-grid"><div><dt>Visible routes</dt><dd>{operationalRoutes.length}</dd></div><div><dt>Ports</dt><dd>2</dd></div><div><dt>Active vessels</dt><dd>1</dd></div><div><dt>View</dt><dd>{viewMode} map</dd></div></dl>
            <div className="corridor-copy"><b>Rotterdam</b><span>→</span><b>PSA Singapore</b></div>
            <div className="legend"><strong>Operational routes</strong>{operationalRoutes.map((route) => {
              const isSelected = route.route_id === selectedRoute?.route_id
              const routeClass = route.route_id === 'RT-001-BASELINE' ? 'baseline' : 'cape'
              return <span className={`legend-route ${isSelected ? 'selected' : 'muted'}`} key={route.route_id}><i className={`legend-line ${routeClass}`} /><span>{routeName(route.route_id)} · {route.distance_nm.toLocaleString()} nm</span>{isSelected && <em>{selectedRoute.is_scheduled_fallback ? 'SCHEDULED' : 'SELECTED'} · {formatEtaDelta(selectedRoute.eta_delta_days)}</em>}</span>
            })}{riskScenario.active && <span><i className="legend-box risk" /> {riskScenario.chokepoint === '—' ? 'No route chokepoint identified' : `${riskScenario.chokepoint} risk`}</span>}</div>
          </div>
        </aside>
        <aside className="scenario-panel floating-panel">
          <div className="floating-title"><span><Activity size={15} /> Risk scenario</span><span className="alert-count">{riskScenario.active ? 'ACTIVE' : 'STANDBY'}</span></div>
          <div className="scenario-list"><div className={`scenario ${riskScenario.active ? 'critical' : ''}`}><span>{riskScenario.title}</span><small>{riskScenario.severity}</small></div></div>
          <div className="scenario-detail"><span>Chokepoint</span><b>{riskScenario.chokepoint}</b><span>Probability</span><b>{riskScenario.probability}</b><span>Duration</span><b>{riskScenario.duration}</b></div>
        </aside>
        <div className="scan-dock"><UrlSubmitForm onRunStarting={startAssessment} onRunCreated={assessmentCreated} onRunStartFailed={assessmentStartFailed} isRunActive={runActive} /></div>
        <section className="bottom-console">
          <RiskTrendStrip runs={recentRuns} activeRun={run} />
          <EventLog events={events} />
        </section>
      </section>

      <aside className="intelligence-rail">
        <div className="rail-head"><div><span className="eyebrow">Human-in-the-loop</span><h1>Agent Activity & Decisions</h1></div><span className="live-badge"><i /> {pipelineLabel}</span></div>
        <section className="run-context-card"><span className="eyebrow">Current assessment</span>{run ? <><strong>{run.event?.entities?.event_type || 'Analysing submitted article'}</strong><p>{run.event?.summary || 'The pipeline is extracting maritime relevance and event entities.'}</p><div><span>Source</span><b>{new URL(run.source_url).hostname}</b><span>Severity</span><b>{run.risk_assessment?.severity || 'Pending'}</b><span>Probability</span><b>{run.risk_assessment ? `${Math.round(run.risk_assessment.probability * 100)}%` : 'Pending'}</b></div></> : <p>Submit one article URL. The five-agent pipeline will assess its relevance to MV Pacific Voyager and the Rotterdam–Singapore corridor.</p>}</section>
        {runId && <div className="active-run-strip"><span>RUN {runId.slice(0, 8)}</span><b className={`status-${status}`}>{isLoading ? 'UPDATING' : status?.replaceAll('_', ' ')}</b></div>}
        <AgentPipelineRail run={pipelineRun} />
        <AdvisoryCard run={run} onDecided={refreshRuns} />
        <RouteComparisonPanel run={run} routes={routes} />
      </aside>
    </div>

    {view !== 'home' && <div className="workspace-overlay" role="dialog" aria-modal="true" aria-label={view === 'history' ? 'History' : 'Route graph viewer'}>
      <button className="workspace-close" onClick={() => setView('home')} aria-label="Close"><X size={16} /> Back to dashboard</button>
      {view === 'history'
        ? <HistoryPanel runs={recentRuns} activeRunId={runId} onSelectRun={openRun} />
        : <RouteGraphViewer routes={routes} vessel={vessel} affectedChokepoints={run?.risk_assessment?.affected_chokepoints || []} />}
    </div>}
  </main>
}
