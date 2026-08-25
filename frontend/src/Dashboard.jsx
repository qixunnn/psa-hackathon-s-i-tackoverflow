import { useCallback, useEffect, useState } from 'react'
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
  const { status, run, events, isLoading } = useRunStream(runId)

  const refreshRuns = useCallback(() => { listRuns().then(setRecentRuns).catch(() => {}) }, [])

  useEffect(() => {
    getRoutes().then(setRoutes).catch(() => {})
    refreshRuns()
  }, [status, refreshRuns])

  useEffect(() => { getVessel().then(setVessel).catch(() => {}) }, [])

  function openRun(nextRunId) {
    setRunId(nextRunId)
    setView('home')
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
        <button className="control-button" onClick={() => document.querySelector('[aria-label="Article URL"]')?.focus()}><RefreshCw size={14} /> New scan</button>
        <div className="view-switch">
          {['2D', '3D'].map((mode) => <button key={mode} className={viewMode === mode ? 'selected' : ''} onClick={() => setViewMode(mode)}>{mode === '2D' ? <Map size={14} /> : <Globe2 size={14} />}{mode}</button>)}
        </div>
        <span className={`system-pill ${routes.length ? '' : 'offline'}`}><i /> {routes.length ? 'API connected' : 'API unavailable'}</span>
      </div>
    </header>

    <div className="command-layout">
      <section className="operations-canvas">
        <MapPanel run={run} routes={routes} viewMode={viewMode} />
        <aside className="map-controls floating-panel">
          <div className="floating-title"><span><Layers3 size={15} /> Map controls</span><ChevronDown size={14} /></div>
          <div className="control-content">
            <div className="control-card-heading"><strong>MVP corridor</strong><span>LIVE</span></div>
            <dl className="map-stat-grid"><div><dt>Graph routes</dt><dd>{routes.length || 3}</dd></div><div><dt>Ports</dt><dd>2</dd></div><div><dt>Active vessels</dt><dd>1</dd></div><div><dt>View</dt><dd>{viewMode} map</dd></div></dl>
            <div className="corridor-copy"><b>Jebel Ali</b><span>→</span><b>PSA Singapore</b></div>
            <div className="legend"><strong>Route graph</strong><span><i className="legend-line baseline" /> Baseline · 3,900 nm</span><span><i className="legend-line bypass" /> Fujairah bypass · 4,100 nm</span><span><i className="legend-line escorted" /> Escorted transit · 3,900 nm</span><span><i className="legend-box risk" /> Hormuz risk zone</span></div>
          </div>
        </aside>
        <aside className="scenario-panel floating-panel">
          <div className="floating-title"><span><Activity size={15} /> Risk scenario</span><span className="alert-count">{run?.risk_assessment ? 'ACTIVE' : 'STANDBY'}</span></div>
          <div className="scenario-list"><div className={`scenario ${run?.risk_assessment ? 'critical' : ''}`}><span>Hormuz tension</span><small>{run?.risk_assessment?.severity || 'AWAITING'}</small></div></div>
          <div className="scenario-detail"><span>Chokepoint</span><b>Strait of Hormuz</b><span>Probability</span><b>{run?.risk_assessment ? `${Math.round(run.risk_assessment.probability * 100)}%` : 'Awaiting scan'}</b><span>Duration</span><b>{run?.risk_assessment?.estimated_duration || 'Awaiting scan'}</b></div>
        </aside>
        <div className="scan-dock"><UrlSubmitForm onRunCreated={setRunId} /></div>
        <section className="bottom-console">
          <RiskTrendStrip runs={recentRuns} activeRun={run} />
          <EventLog events={events} />
        </section>
      </section>

      <aside className="intelligence-rail">
        <div className="rail-head"><div><span className="eyebrow">Human-in-the-loop</span><h1>Agent Activity & Decisions</h1></div><span className="live-badge"><i /> {runId ? 'RUNNING' : 'READY'}</span></div>
        <section className="run-context-card"><span className="eyebrow">Current assessment</span>{run ? <><strong>{run.event?.entities?.event_type || 'Analysing submitted article'}</strong><p>{run.event?.summary || 'The pipeline is extracting maritime relevance and event entities.'}</p><div><span>Source</span><b>{new URL(run.source_url).hostname}</b><span>Severity</span><b>{run.risk_assessment?.severity || 'Pending'}</b><span>Probability</span><b>{run.risk_assessment ? `${Math.round(run.risk_assessment.probability * 100)}%` : 'Pending'}</b></div></> : <p>Submit one article URL. The five-agent pipeline will assess its relevance to MV Pacific Voyager and the Jebel Ali–Singapore corridor.</p>}</section>
        {runId && <div className="active-run-strip"><span>RUN {runId.slice(0, 8)}</span><b className={`status-${status}`}>{isLoading ? 'UPDATING' : status?.replaceAll('_', ' ')}</b></div>}
        <AgentPipelineRail run={run} />
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
