import { useEffect, useRef } from 'react'

export default function EventLog({ events = [] }) {
  const logRef = useRef(null)
  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' }) }, [events])
  return <section className="panel event-log"><div className="section-heading"><div><span className="eyebrow">Audit trail</span><h2>System event log</h2></div><span className="count-badge">{events.length}</span></div><div className="event-list" ref={logRef}>{events.length === 0 ? <p className="empty-state">Waiting for pipeline activity...</p> : events.map((event, index) => <div className="event-row" key={`${event.timestamp}-${index}`}><time>{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time><div><strong>{event.agent.replaceAll('_', ' ')}</strong><p>{event.message}</p></div></div>)}</div></section>
}
