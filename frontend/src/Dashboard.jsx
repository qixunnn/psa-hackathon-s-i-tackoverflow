import { useEffect, useState } from 'react'
import UrlSubmitForm from './components/UrlSubmitForm'
import AgentPipelineRail from './components/AgentPipelineRail'
import EventLog from './components/EventLog'
import AdvisoryCard from './components/AdvisoryCard'
import RouteComparisonPanel from './components/RouteComparisonPanel'
import MapPanel from './components/MapPanel'
import RiskTrendStrip from './components/RiskTrendStrip'
import { getRoutes, listRuns } from './lib/api'
import { useRunStream } from './lib/useRunStream'

export default function Dashboard() {
  const [runId, setRunId] = useState(null)
  const [routes, setRoutes] = useState([])
  const [recentRuns, setRecentRuns] = useState([])
  const { status, run, events, isLoading } = useRunStream(runId)

  useEffect(() => {
    getRoutes().then(setRoutes).catch(() => {})
    listRuns().then(setRecentRuns).catch(() => {})
  }, [status])

  return <main className="dashboard-shell"><header className="topbar"><div className="brand-lockup"><span className="brand-mark">PS</span><div><strong>PSA Sentinel</strong><span>Maritime risk intelligence</span></div></div><div className="topbar-status"><span className="live-dot" /> Operations desk <span className="utc">UTC</span></div></header><div className="dashboard-content"><UrlSubmitForm onRunCreated={setRunId} />{runId && <><div className="run-banner"><div><span className="eyebrow">Active run</span><strong>{runId}</strong></div><span className={`run-status status-${status}`}>{isLoading ? 'Updating' : status?.replaceAll('_', ' ')}</span></div><AgentPipelineRail run={run} /><div className="dashboard-grid"><div className="main-column"><MapPanel run={run} /><RouteComparisonPanel run={run} routes={routes} /></div><div className="side-column"><AdvisoryCard run={run} /><EventLog events={events} /></div></div><RiskTrendStrip runs={recentRuns} /></>}</div></main>
}
