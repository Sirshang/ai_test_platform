import client from './client'

export function fetchProjects() {
  return client.get('/projects/')
}

export function fetchProject(id) {
  return client.get(`/projects/${id}/`)
}

export function createProject(payload) {
  return client.post('/projects/', payload)
}

export function updateProject(id, payload) {
  return client.patch(`/projects/${id}/`, payload)
}

export function deleteProject(id) {
  return client.delete(`/projects/${id}/`)
}
