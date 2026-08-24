import { useState } from 'react'
import { submitDecision } from '../lib/api'

export default function AdvisoryCard({ run }) {
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [decision, setDecision] = useState(run?.advisory?.operator_decision !== 'pending' ? run?.advisory?.operator_decision : null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  if (!run) return <section className="panel advisory-card empty-state">Advisory will appear when the run completes.</section>
  if (run.status === 'halted_not_relevant') return <section className="panel neutral-outcome"><span className="eyebrow">Assessment complete</span><h2>No PSA impact detected</h2><p>{run.event?.summary}</p><div className="confidence-line"><span>Rationale confidence</span><strong>{Math.round((run.event?.confidence || 0) * 100)}%</strong></div></section>
  const advisory = run.advisory
  if (!advisory) return <section className="panel advisory-card empty-state">Advisory will appear when the run completes.</section>
  const decided = Boolean(decision)
  async function handleDecision(nextDecision) {
    setDecision(nextDecision)
    setIsSubmitting(true)
    try { await submitDecision(run.run_id, nextDecision, null) } finally { setIsSubmitting(false) }
  }
  return <section className="panel advisory-card"><div className="section-heading"><span className="eyebrow">Operator advisory</span><span className="confidence-badge">{Math.round(advisory.confidence * 100)}% confidence</span></div><h2>{advisory.headline}</h2><p className="advisory-summary">{advisory.summary}</p><div className="actions-list">{advisory.recommended_actions.map((action) => <label key={action}><input type="checkbox" />{action}</label>)}</div><div className="decision-actions"><button className="accept-button" onClick={() => handleDecision('accepted')} disabled={decided || isSubmitting}>Accept</button><button className="dismiss-button" onClick={() => handleDecision('dismissed')} disabled={decided || isSubmitting}>Dismiss</button><button className="detail-button" onClick={() => setDetailsOpen(!detailsOpen)}>{detailsOpen ? 'Hide detail' : 'Request more detail'}</button></div>{decision && <p className="decision-note">Decision recorded: {decision}</p>}{detailsOpen && <div className="detail-drawer"><strong>Risk rationale</strong><p>{run.risk_assessment?.rationale}</p><strong>Route reasoning</strong>{run.ranked_routes?.map((route) => <p key={route.route_id}><b>{route.route_id}:</b> {route.rationale}</p>)}</div>}</section>
}
