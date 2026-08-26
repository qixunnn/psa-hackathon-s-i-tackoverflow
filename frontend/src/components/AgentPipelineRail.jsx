const AGENTS = [
  ['Relevance & Extraction', 'event'],
  ['Risk & Severity', 'risk_assessment'],
  ['Route Retrieval', 'candidate_routes'],
  ['Ranking & Impact', 'ranked_routes'],
  ['Advisory & Recommendation', 'advisory'],
]

const STATUS_AGENT_INDEX = {
  extracting: 0,
  awaiting_manual_text: 0,
  assessing_risk: 1,
  retrieving_routes: 2,
  ranking: 3,
  advising: 4,
}

function getAgentStatus(run, field, index) {
  if (!run) return index === 0 ? 'idle' : 'waiting'
  if (run?.[field]) return 'done'
  if (run?.status === 'error') {
    const firstMissing = AGENTS.findIndex(([, outputField]) => !run[outputField])
    return index === firstMissing ? 'error' : 'queued'
  }
  if (run?.status === 'complete') return 'done'
  if (run?.status === 'halted_not_relevant') return index === 0 ? 'done' : 'queued'
  if (run?.status === 'queued') return index === 0 ? 'queued' : 'waiting'
  if (run?.status === 'awaiting_manual_text') return index === 0 ? 'waiting' : 'queued'
  const activeIndex = STATUS_AGENT_INDEX[run?.status]
  if (activeIndex !== undefined) {
    if (index < activeIndex) return 'done'
    if (index === activeIndex) return 'running'
    return 'queued'
  }
  return 'queued'
}

export default function AgentPipelineRail({ run }) {
  return (
    <section className="rail-section">
      <div className="section-heading"><span className="eyebrow">Pipeline</span><span className="live-dot">Live sequence</span></div>
      <div className="agent-rail">
        {AGENTS.map(([label, field], index) => {
          const status = getAgentStatus(run, field, index)
          return <article className={`agent-card agent-${status}`} key={label}><span className="agent-index">0{index + 1}</span><div><h3>{label}</h3><p>{status}</p></div><span className="status-mark" /></article>
        })}
      </div>
    </section>
  )
}
