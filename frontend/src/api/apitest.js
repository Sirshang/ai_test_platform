import client from './client'

export function fetchApiCases(projectId) {
  return client.get('/api-cases/', { params: { project: projectId } })
}

export function fetchApiCase(id) {
  return client.get(`/api-cases/${id}/`)
}

export function createApiCase(payload) {
  return client.post('/api-cases/', payload)
}

export function updateApiCase(id, payload) {
  return client.patch(`/api-cases/${id}/`, payload)
}

export function deleteApiCase(id) {
  return client.delete(`/api-cases/${id}/`)
}

export function importSwagger(projectId, payload) {
  return client.post(`/projects/${projectId}/import-swagger/`, payload)
}

export function generateApiScript(payload) {
  return client.post('/ai/generate-api-script/', payload, { timeout: 120000 })
}
