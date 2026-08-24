import { useEffect, useState } from 'react'
import {
  Activity, Bell, Bot, ChevronDown, CircleUserRound, Globe2, Home,
  Layers3, Map, Radio, RefreshCw, Search, Settings, ShieldCheck, Sparkles,
} from 'lucide-react'
import UrlSubmitForm from './components/UrlSubmitForm'
import AgentPipelineRail from './components/AgentPipelineRail'
import EventLog from './components/EventLog'
import AdvisoryCard from './components/AdvisoryCard'
import MapPanel from './components/MapPanel'
import RiskTrendStrip from './components/RiskTrendStrip'
import RouteComparisonPanel from './components/RouteComparisonPanel'
import { getRoutes, listRuns } from './lib/api'
import { useRunStream } from './lib/useRunStream'

function EngineCard({ icon: Icon, name, subtitle, progress, children, tone = 'blue' }) {
  return <article className="engine-card">
    <div className={`engine-icon ${tone}`}><Icon size={17} /></div>
    <div className="engine-body">
      <div className="engine-heading"><strong>{name}</strong><span>PROCESSING</span></div>
      <p>{subtitle}</p>
      <div className="engine-progress"><i style={{ width: `${progress}%` }} /></div>
      <small>{children}</small>
    </div>
  </article>
}

export default function Dashboard() {
  const [runId, setRunId] = useState(null)
  const [routes, setRoutes] = useState([])
  const [recentRuns, setRecentRuns] = useState([])
  const [viewMode, setViewMode] = useState('2D')
  const { status, run, events, isLoading } = useRunStream(runId)

  useEffect(() => {
    getRoutes().then(setRoutes).catch(() => {})
    listRuns().then(setRecentRuns).catch(() => {})
  }, [status])

  return <main className="command-shell">
    <header className="command-header">
      <div className="header-left">
        <div className="shield-logo"><ShieldCheck size={20} /></div>
        <nav className="primary-nav" aria-label="Primary navigation">
          <button className="nav-button active"><Home size={15} /> Home</button>
          <button className="nav-button"><Settings size={15} /> Admin</button>
        </nav>
        <div className="product-title"><strong>PSA Sentinel</strong><span>Agentic supply-chain risk advisory</span></div>
      </div>
      <div className="header-actions">
        <button className="control-button quiet"><Radio size={14} /> Pipeline live</button>
        <button className="control-button"><RefreshCw size={14} /> New scan</button>
        <div className="view-switch">
          {['2D', '3D'].map((mode) => <button key={mode} className={viewMode === mode ? 'selected' : ''} onClick={() => setViewMode(mode)}>{mode === '2D' ? <Map size={14} /> : <Globe2 size={14} />}{mode}</button>)}
        </div>
        <span className={`system-pill ${routes.length ? '' : 'offline'}`}><i /> {routes.length ? 'API connected' : 'API unavailable'}</span>
        <button className="icon-button" aria-label="Notifications"><Bell size={16} /></button>
        <CircleUserRound className="user-avatar" size={26} />
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
          <div className="floating-title"><span><Activity size={15} /> Active scenario</span><span className="alert-count">MVP</span></div>
          <div className="scenario-list"><button className="scenario critical"><span>Hormuz tension</span><small>{run?.risk_assessment?.severity || 'DEMO'}</small></button></div>
          <div className="scenario-detail"><span>Chokepoint</span><b>Strait of Hormuz</b><span>Probability</span><b>{run?.risk_assessment ? `${Math.round(run.risk_assessment.probability * 100)}%` : 'Awaiting scan'}</b><span>Duration</span><b>{run?.risk_assessment?.estimated_duration || 'Awaiting scan'}</b></div>
        </aside>
        <div className="scan-dock"><UrlSubmitForm onRunCreated={setRunId} /></div>
        <section className="bottom-console">
          <RiskTrendStrip runs={recentRuns} activeRun={run} />
          <EventLog events={events} />
        </section>
      </section>

      <aside className="intelligence-rail">
        <div className="rail-head"><div><span className="eyebrow">Command intelligence</span><h1>Operational Copilot</h1></div><span className="live-badge"><i /> LIVE</span></div>
        <div className="rail-search"><Search size={15} /><span>Monitoring global maritime signals</span><Sparkles size={14} /></div>
        <div className="engine-stack">
          <EngineCard icon={Search} name="Relevance & extraction" subtitle="Agent 1 · article analysis" progress={run?.event ? 100 : isLoading ? 55 : 0}>Ready for a manually submitted article URL.</EngineCard>
          <EngineCard icon={Bot} name="Risk & severity" subtitle="Agent 2 · disruption assessment" progress={run?.risk_assessment ? 100 : run?.event ? 42 : 0} tone="violet">Evaluates severity, probability and affected chokepoints.</EngineCard>
        </div>
        <div className="reasoning-head"><span><Bot size={15} /> Agent reasoning</span><b><i /> LIVE</b></div>
        <div className="reasoning-tabs"><button className="active">Reasoning <span>{events.length || 3}</span></button><button>Decision</button><button>Execution</button></div>
        {runId && <div className="active-run-strip"><span>RUN {runId.slice(0, 8)}</span><b className={`status-${status}`}>{isLoading ? 'UPDATING' : status?.replaceAll('_', ' ')}</b></div>}
        <AgentPipelineRail run={run} />
        <AdvisoryCard run={run} />
        <RouteComparisonPanel run={run} routes={routes} />
      </aside>
    </div>
  </main>
}
