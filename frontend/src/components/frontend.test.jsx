import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import UrlSubmitForm from './UrlSubmitForm'
import AgentPipelineRail from './AgentPipelineRail'
import AdvisoryCard from './AdvisoryCard'
import HistoryPanel from './HistoryPanel'
import RouteComparisonPanel from './RouteComparisonPanel'
import RouteGraphViewer from './RouteGraphViewer'
import { submitDecision, submitRun } from '../lib/api'

vi.mock('../lib/api', () => ({
  submitRun: vi.fn(),
  submitDecision: vi.fn(() => Promise.resolve()),
}))

beforeEach(() => vi.clearAllMocks())

describe('UrlSubmitForm', () => {
  it('submits entered values and disables while pending', async () => {
    let resolveRequest
    submitRun.mockReturnValue(new Promise((resolve) => { resolveRequest = resolve }))
    render(<UrlSubmitForm onRunCreated={vi.fn()} />)
    fireEvent.change(screen.getByLabelText('Article URL'), { target: { value: 'https://example.com/story' } })
    fireEvent.change(screen.getByLabelText('Operator note'), { target: { value: 'Watch closely' } })
    fireEvent.click(screen.getByRole('button', { name: 'Start assessment' }))
    expect(submitRun).toHaveBeenCalledWith('https://example.com/story', 'Watch closely')
    expect(screen.getByRole('button', { name: 'Submitting...' })).toBeDisabled()
    resolveRequest({ run_id: 'run-1' })
    await waitFor(() => expect(screen.getByRole('button', { name: 'Start assessment' })).toBeEnabled())
  })
})

describe('AgentPipelineRail', () => {
  it('derives done, running, and queued statuses from accumulated run data', () => {
    render(<AgentPipelineRail run={{ status: 'assessing_risk', event: { relevant: true } }} />)
    expect(screen.getByText('Relevance & Extraction').nextElementSibling).toHaveTextContent('done')
    expect(screen.getByText('Risk & Severity').nextElementSibling).toHaveTextContent('running')
    expect(screen.getByText('Route Retrieval').nextElementSibling).toHaveTextContent('queued')
    expect(screen.getByText('Ranking & Impact').nextElementSibling).toHaveTextContent('queued')
    expect(screen.getByText('Advisory & Recommendation').nextElementSibling).toHaveTextContent('queued')
  })

  it('uses pipeline status to avoid stale running states before refreshed output arrives', () => {
    render(<AgentPipelineRail run={{ status: 'assessing_risk' }} />)
    expect(screen.getByText('Relevance & Extraction').nextElementSibling).toHaveTextContent('done')
    expect(screen.getByText('Risk & Severity').nextElementSibling).toHaveTextContent('running')
  })
})

describe('AdvisoryCard', () => {
  const completeRun = { run_id: 'run-1', status: 'complete', advisory: { headline: 'Delay risk', summary: 'Review the voyage.', confidence: 0.85, recommended_actions: ['Review berth'], operator_decision: 'pending' }, risk_assessment: { rationale: 'Risk rationale' }, ranked_routes: [] }

  it('renders a neutral not-relevant outcome without decisions', () => {
    render(<AdvisoryCard run={{ status: 'halted_not_relevant', event: { summary: 'Domestic labor dispute.', confidence: 0.92 } }} />)
    expect(screen.getByText('No PSA impact detected')).toBeInTheDocument()
    expect(screen.getByText('Domestic labor dispute.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Accept' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Dismiss' })).not.toBeInTheDocument()
  })

  it('submits an accepted decision and disables both decision buttons', async () => {
    render(<AdvisoryCard run={completeRun} />)
    fireEvent.click(screen.getByRole('button', { name: 'Accept' }))
    expect(submitDecision).toHaveBeenCalledWith('run-1', 'accepted', null)
    expect(screen.getByRole('button', { name: 'Accept' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Dismiss' })).toBeDisabled()
    await waitFor(() => expect(screen.getByText(/Decision recorded: accepted/)).toBeInTheDocument())
  })

  it('records an operator comment alongside the decision', async () => {
    render(<AdvisoryCard run={completeRun} />)
    fireEvent.change(screen.getByLabelText('Operator comment'), { target: { value: 'Berth slot already held.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss' }))
    expect(submitDecision).toHaveBeenCalledWith('run-1', 'dismissed', 'Berth slot already held.')
    await waitFor(() => expect(screen.getByText(/Berth slot already held\./)).toBeInTheDocument())
  })

  it('locks controls for a run that was already decided in an earlier session', async () => {
    const decidedRun = { ...completeRun, advisory: { ...completeRun.advisory, operator_decision: 'accepted', operator_comment: 'Actioned by duty desk.' } }
    const { rerender } = render(<AdvisoryCard run={null} />)
    rerender(<AdvisoryCard run={decidedRun} />)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Accept' })).toBeDisabled())
    expect(screen.getByRole('button', { name: 'Dismiss' })).toBeDisabled()
    expect(screen.getByText(/Actioned by duty desk\./, { selector: 'em' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Override' }))
    expect(screen.getByRole('button', { name: 'Dismiss' })).toBeEnabled()
  })

  it('flags a low-confidence advisory for mandatory review', () => {
    render(<AdvisoryCard run={{ ...completeRun, advisory: { ...completeRun.advisory, confidence: 0.42 } }} />)
    expect(screen.getByText(/mandatory human review/i)).toBeInTheDocument()
  })
})

describe('HistoryPanel', () => {
  const runs = [
    { run_id: 'run-2', source_url: 'https://news.example/hormuz', status: 'complete', submitted_at: '2026-08-02T10:00:00Z', relevant: true, severity: 'High', probability: 0.7, headline: 'Delay risk', operator_decision: 'accepted' },
    { run_id: 'run-1', source_url: 'https://news.example/local', status: 'halted_not_relevant', submitted_at: '2026-08-01T10:00:00Z', relevant: false, severity: null, probability: null, headline: null, operator_decision: null },
  ]

  it('renders each past run with its outcome and drills down on demand', () => {
    const onSelectRun = vi.fn()
    render(<HistoryPanel runs={runs} activeRunId="run-2" onSelectRun={onSelectRun} />)
    expect(screen.getByText('Advisory issued')).toBeInTheDocument()
    expect(screen.getByText('No PSA impact')).toBeInTheDocument()
    expect(screen.getByText('accepted')).toBeInTheDocument()
    expect(screen.getByText('70%')).toBeInTheDocument()

    fireEvent.click(screen.getAllByRole('button', { name: 'Open' })[1])
    expect(onSelectRun).toHaveBeenCalledWith('run-1')
  })

  it('explains the empty audit trail instead of rendering a bare table', () => {
    render(<HistoryPanel runs={[]} onSelectRun={vi.fn()} />)
    expect(screen.getByText(/No runs recorded yet/)).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })
})

describe('RouteGraphViewer', () => {
  const routes = [
    { route_id: 'RT-001-BASELINE', origin: 'Jebel Ali', destination: 'PSA Singapore', waypoints: ['Jebel Ali', 'Strait of Hormuz', 'PSA Singapore'], chokepoints: ['Strait of Hormuz'], distance_nm: 3900, base_transit_days: 11 },
    { route_id: 'RT-002-FUJAIRAH-BYPASS', origin: 'Jebel Ali', destination: 'PSA Singapore', waypoints: ['Jebel Ali', 'Gulf of Oman', 'PSA Singapore'], chokepoints: [], distance_nm: 4100, base_transit_days: 13 },
  ]

  it('marks the scheduled baseline and the routes exposed to the live risk', () => {
    render(<RouteGraphViewer routes={routes} vessel={{ vessel_name: 'MV Pacific Voyager', scheduled_route_id: 'RT-001-BASELINE', scheduled_arrival: '2026-09-04T16:26:26Z' }} affectedChokepoints={['Strait of Hormuz']} />)
    expect(screen.getByText('Scheduled baseline')).toBeInTheDocument()
    expect(screen.getByText('Exposed')).toBeInTheDocument()
    expect(screen.getByText('3,900 nm')).toBeInTheDocument()
    expect(screen.getByText('MV Pacific Voyager')).toBeInTheDocument()
  })

  it('states the graph is lookup-only so judges see the agent cannot invent routes', () => {
    render(<RouteGraphViewer routes={routes} />)
    expect(screen.getByText(/never route invention/i)).toBeInTheDocument()
    expect(screen.queryByText('Exposed')).not.toBeInTheDocument()
  })
})

describe('RouteComparisonPanel', () => {
  it('joins ranked routes to graph routes by route_id', () => {
    render(<RouteComparisonPanel run={{ ranked_routes: [{ route_id: 'RT-002', rank: 1, eta: '2026-09-01T00:00:00Z', eta_delta_days: 2 }, { route_id: 'RT-001', rank: 2, eta: '2026-08-30T00:00:00Z', eta_delta_days: 0 }] }} routes={[{ route_id: 'RT-002', distance_nm: 4100, base_transit_days: 13, chokepoints: ['Malacca'] }, { route_id: 'RT-001', distance_nm: 3900, base_transit_days: 11, chokepoints: ['Hormuz'] }]} />)
    expect(screen.getByText(/RT-002/)).toBeInTheDocument()
    expect(screen.getByText('4100')).toBeInTheDocument()
    expect(screen.getByText('13')).toBeInTheDocument()
    expect(screen.getByText(/RT-001/)).toBeInTheDocument()
    expect(screen.getByText('3900')).toBeInTheDocument()
    expect(screen.getByText('11')).toBeInTheDocument()
  })
})
