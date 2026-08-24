const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`)
  }
  return response.json()
}

export function submitRun(sourceUrl, note) {
  return request('/runs', {
    method: 'POST',
    body: JSON.stringify({ source_url: sourceUrl, note: note || null }),
  })
}

export function getRun(runId) {
  return request(`/runs/${runId}`)
}

export function getRunEvents(runId) {
  return request(`/runs/${runId}/events`)
}

export function getRoutes() {
  return request('/routes')
}

export function listRuns() {
  return request('/runs')
}

export function submitDecision(runId, decision, comment) {
  return request(`/runs/${runId}/decision`, {
    method: 'POST',
    body: JSON.stringify({ decision, comment: comment || null }),
  })
}

export { API_BASE_URL }
