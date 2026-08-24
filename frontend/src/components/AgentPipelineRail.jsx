const AGENTS = [
  ['Relevance & Extraction', 'event'],
  ['Risk & Severity', 'risk_assessment'],
  ['Route Retrieval', 'candidate_routes'],
  ['Ranking & Impact', 'ranked_routes'],
  ['Advisory & Recommendation', 'advisory'],
]

const RUNNING_STATES = ['extracting', 'assessing_risk', 'retrieving_routes', 'ranking', 'advising']

function getAgentStatus(run, field, index) {
  if (run?.[field]) return 'done'
  if (run?.status === 'error') {
    const firstMissing = AGENTS.findIndex(([, outputField]) => !run[outputField])
    return index === firstMissing ? 'error' : 'queued'
  }
  const nextMissing = AGENTS.findIndex(([, outputField]) => !run?.[outputField])
  if (index === nextMissing && (!run?.status || RUNNING_STATES.includes(run.status))) return 'running'
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
