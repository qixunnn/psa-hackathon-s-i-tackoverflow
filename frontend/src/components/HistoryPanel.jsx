const OUTCOME = {
  complete: { label: 'Advisory issued', tone: 'ok' },
  halted_not_relevant: { label: 'No PSA impact', tone: 'neutral' },
  error: { label: 'Pipeline error', tone: 'bad' },
  awaiting_manual_text: { label: 'Needs article text', tone: 'warn' },
}

const DECISION = { accepted: 'ok', dismissed: 'bad', pending: 'warn' }

function hostname(url) {
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}

export default function HistoryPanel({ runs = [], activeRunId, onSelectRun }) {
  return <section className="workspace-view">
    <div className="workspace-head">
      <div><span className="eyebrow">Auditability</span><h2>History · past runs</h2></div>
      <span className="count-badge">{runs.length} runs</span>
    </div>
    {runs.length === 0
      ? <p className="empty-state">No runs recorded yet. Submit an article from Home to build the audit trail.</p>
      : <div className="workspace-table-wrap">
          <table className="workspace-table">
            <thead>
              <tr>
                <th>Submitted</th><th>Source</th><th>Outcome</th><th>Relevant</th>
                <th>Severity</th><th>Probability</th><th>Advisory</th><th>Decision</th><th />
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => {
                const outcome = OUTCOME[run.status] || { label: run.status.replaceAll('_', ' '), tone: 'warn' }
                return <tr key={run.run_id} className={run.run_id === activeRunId ? 'active-row' : ''}>
                  <td><time dateTime={run.submitted_at}>{new Date(run.submitted_at).toLocaleString()}</time></td>
                  <td className="truncate" title={run.source_url}>{hostname(run.source_url)}</td>
                  <td><span className={`tag ${outcome.tone}`}>{outcome.label}</span></td>
                  <td>{run.relevant === undefined || run.relevant === null ? '—' : run.relevant ? 'Yes' : 'No'}</td>
                  <td>{run.severity || '—'}</td>
                  <td>{typeof run.probability === 'number' ? `${Math.round(run.probability * 100)}%` : '—'}</td>
                  <td className="truncate" title={run.headline || ''}>{run.headline || '—'}</td>
                  <td>{run.operator_decision
                    ? <span className={`tag ${DECISION[run.operator_decision] || 'warn'}`}>{run.operator_decision}</span>
                    : '—'}</td>
                  <td><button className="detail-button" onClick={() => onSelectRun(run.run_id)}>Open</button></td>
                </tr>
              })}
            </tbody>
          </table>
        </div>}
  </section>
}
