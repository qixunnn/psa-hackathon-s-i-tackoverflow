import { useEffect, useState } from 'react'
import { submitDecision } from '../lib/api'

// Below this, 5.4 requires the advisory be flagged for mandatory human review
// rather than surfaced as fact.
const LOW_CONFIDENCE_THRESHOLD = 0.6

function settled(advisory) {
  const decision = advisory?.operator_decision
  return decision && decision !== 'pending' ? decision : null
}

export default function AdvisoryCard({ run, onDecided }) {
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [decision, setDecision] = useState(() => settled(run?.advisory))
  const [comment, setComment] = useState('')
  const [isOverriding, setIsOverriding] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Runs load asynchronously and History can swap the run underneath us, so the
  // persisted decision — not just the first render's — drives the controls.
  const persisted = settled(run?.advisory)
  const runId = run?.run_id
  useEffect(() => {
    setDecision(persisted)
    setComment(run?.advisory?.operator_comment || '')
    setIsOverriding(false)
    setError('')
  }, [runId, persisted, run?.advisory?.operator_comment])

  if (!run) return <section className="panel advisory-card empty-state">Advisory will appear when the run completes.</section>
  if (run.status === 'halted_not_relevant') return <section className="panel neutral-outcome"><span className="eyebrow">Assessment complete</span><h2>No PSA impact detected</h2><p>{run.event?.summary}</p><div className="confidence-line"><span>Rationale confidence</span><strong>{Math.round((run.event?.confidence || 0) * 100)}%</strong></div></section>

  const advisory = run.advisory
  if (!advisory) return <section className="panel advisory-card empty-state">Advisory will appear when the run completes.</section>

  const locked = Boolean(decision) && !isOverriding
  const lowConfidence = advisory.confidence < LOW_CONFIDENCE_THRESHOLD

  async function handleDecision(nextDecision) {
    const trimmed = comment.trim()
    setIsSubmitting(true)
    setError('')
    try {
      await submitDecision(run.run_id, nextDecision, trimmed || null)
      setDecision(nextDecision)
      setIsOverriding(false)
      onDecided?.()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return <section className={`panel advisory-card ${lowConfidence ? 'low-confidence' : ''}`}>
    <div className="section-heading">
      <span className="eyebrow">Operator advisory</span>
      <span className="confidence-badge">{Math.round(advisory.confidence * 100)}% confidence</span>
    </div>
    {lowConfidence && <p className="review-flag" role="status">Low confidence — mandatory human review before this is treated as actioned.</p>}
    <h2>{advisory.headline}</h2>
    <p className="advisory-summary">{advisory.summary}</p>
    <div className="actions-list">
      {advisory.recommended_actions.map((action) => <label key={action}><input type="checkbox" />{action}</label>)}
    </div>

    <div className="decision-panel">
      <label className="decision-comment">
        Operator comment <span>(optional, recorded with the decision)</span>
        <textarea
          aria-label="Operator comment"
          value={comment}
          rows="2"
          disabled={locked || isSubmitting}
          placeholder="Why you accepted or dismissed this advisory"
          onChange={(event) => setComment(event.target.value)}
        />
      </label>
      <div className="decision-actions">
        <button className="accept-button" onClick={() => handleDecision('accepted')} disabled={locked || isSubmitting}>Accept</button>
        <button className="dismiss-button" onClick={() => handleDecision('dismissed')} disabled={locked || isSubmitting}>Dismiss</button>
        <button className="detail-button" onClick={() => setDetailsOpen(!detailsOpen)}>{detailsOpen ? 'Hide detail' : 'Request more detail'}</button>
      </div>
      {decision && !isOverriding && <p className="decision-note">
        Decision recorded: {decision}
        {(comment.trim() || advisory.operator_comment) && <em> — “{comment.trim() || advisory.operator_comment}”</em>}
        <button className="link-button" onClick={() => setIsOverriding(true)}>Override</button>
      </p>}
      {error && <p className="form-error">{error}</p>}
    </div>

    {detailsOpen && <div className="detail-drawer">
      <strong>Risk rationale</strong>
      <p>{run.risk_assessment?.rationale}</p>
      <strong>Route reasoning</strong>
      {run.ranked_routes?.map((route) => <p key={route.route_id}><b>{route.route_id}:</b> {route.rationale}</p>)}
    </div>}
  </section>
}
