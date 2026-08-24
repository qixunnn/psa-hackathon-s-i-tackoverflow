import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import UrlSubmitForm from './UrlSubmitForm'
import AgentPipelineRail from './AgentPipelineRail'
import AdvisoryCard from './AdvisoryCard'
import RouteComparisonPanel from './RouteComparisonPanel'
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
