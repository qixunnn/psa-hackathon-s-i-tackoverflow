import { useEffect, useRef } from 'react'

const standbyEvents = [
  { timestamp: '2026-08-25T00:43:00Z', agent: 'orchestrator', message: 'Pipeline ready; awaiting manual article submission.' },
  { timestamp: '2026-08-25T00:42:00Z', agent: 'route_graph', message: 'Three validated Jebel Ali–Singapore routes available.' },
  { timestamp: '2026-08-25T00:41:00Z', agent: 'vessel_schedule', message: 'MV Pacific Voyager schedule loaded for 04 September.' },
]

export default function EventLog({ events = [] }) {
  const logRef = useRef(null)
  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' }) }, [events])
  const visibleEvents = events.length ? events : standbyEvents
  return <section className="panel event-log"><div className="section-heading"><div><span className="eyebrow">Audit trail</span><h2>System event log</h2></div><span className="count-badge">{events.length ? events.length : 'standby'}</span></div><div className="event-list" ref={logRef}>{visibleEvents.map((event, index) => <div className="event-row" key={`${event.timestamp}-${index}`}><time>{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time><div><strong>{event.agent.replaceAll('_', ' ')}</strong><p>{event.message}</p></div></div>)}</div></section>
}
