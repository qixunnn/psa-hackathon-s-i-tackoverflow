import { useEffect, useState } from 'react'
import { API_BASE_URL, getRun, getRunEvents } from './api'

const TERMINAL_STATUSES = new Set(['complete', 'halted_not_relevant', 'error'])

export function useRunStream(runId) {
  const [state, setState] = useState({ status: null, run: null, events: [], isLoading: false })

  useEffect(() => {
    if (!runId) {
      setState({ status: null, run: null, events: [], isLoading: false })
      return undefined
    }

    let closed = false
    let source
    const refresh = async (statusHint) => {
      setState((current) => ({ ...current, isLoading: true, status: statusHint || current.status }))
      try {
        const [run, events] = await Promise.all([getRun(runId), getRunEvents(runId)])
        if (!closed) {
          setState({ status: run.status, run, events, isLoading: false })
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
        setState((current) => ({
          ...current,
          status,
          run: current.run ? { ...current.run, status } : current.run,
        }))
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

  return state
}
