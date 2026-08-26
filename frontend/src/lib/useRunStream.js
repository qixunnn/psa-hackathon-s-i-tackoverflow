import { useEffect, useState } from 'react'
import { API_BASE_URL, getRun, getRunEvents } from './api'

const TERMINAL_STATUSES = new Set(['complete', 'halted_not_relevant', 'error'])
const EMPTY_STATE = { runId: null, status: null, run: null, events: [], isLoading: false }

export function useRunStream(runId) {
  const [state, setState] = useState(EMPTY_STATE)

  useEffect(() => {
    if (!runId) {
      setState(EMPTY_STATE)
      return undefined
    }

    let closed = false
    let source
    setState({ ...EMPTY_STATE, runId, isLoading: true })
    const refresh = async (statusHint) => {
      setState((current) => current.runId === runId
        ? { ...current, isLoading: true, status: statusHint || current.status }
        : current)
      try {
        const [run, events] = await Promise.all([getRun(runId), getRunEvents(runId)])
        if (!closed) {
          setState({ runId, status: run.status, run, events, isLoading: false })
          if (TERMINAL_STATUSES.has(run.status)) source?.close()
        }
      } catch {
        if (!closed) setState((current) => ({ ...current, isLoading: false }))
      }
    }

    refresh()
    source = new EventSource(`${API_BASE_URL}/runs/${runId}/stream`)
    source.onmessage = (message) => {
      let status
      try {
        status = JSON.parse(message.data).status
      } catch {
        status = undefined
      }
      if (status) {
        setState((current) => current.runId === runId ? ({
          ...current,
          status,
          run: current.run ? { ...current.run, status } : current.run,
        }) : current)
      }
      refresh(status)
      if (TERMINAL_STATUSES.has(status)) source.close()
    }
    source.onerror = () => {
      if (!closed) setState((current) => ({ ...current, isLoading: false }))
    }

    return () => {
      closed = true
      source?.close()
    }
  }, [runId])

  return state.runId === runId
    ? state
    : { ...EMPTY_STATE, runId, isLoading: Boolean(runId) }
}
