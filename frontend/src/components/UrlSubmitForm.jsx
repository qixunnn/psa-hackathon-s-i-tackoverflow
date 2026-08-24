import { useState } from 'react'
import { submitRun } from '../lib/api'

export default function UrlSubmitForm({ onRunCreated }) {
  const [sourceUrl, setSourceUrl] = useState('')
  const [note, setNote] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')
    try {
      const result = await submitRun(sourceUrl, note)
      onRunCreated(result.run_id)
      setSourceUrl('')
      setNote('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="submit-form" onSubmit={handleSubmit}>
      <div className="form-copy">
        <span className="eyebrow">New intelligence run</span>
        <h2>Scan an article for schedule risk</h2>
      </div>
      <label>
        Article URL
        <input aria-label="Article URL" type="url" required value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} placeholder="https://newsroom.example/article" disabled={isSubmitting} />
      </label>
      <label>
        Operator note <span>(optional)</span>
        <textarea aria-label="Operator note" value={note} onChange={(event) => setNote(event.target.value)} placeholder="Context from the duty desk" rows="1" disabled={isSubmitting} />
      </label>
      <button className="primary-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Submitting...' : 'Start assessment'}</button>
      {error && <p className="form-error">{error}</p>}
    </form>
  )
}
