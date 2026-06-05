import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function setAuthCredentials(username, password) {
  if (username && password) {
    client.defaults.auth = { username, password }
  } else {
    delete client.defaults.auth
  }
}

export function getErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.join('；')
  if (typeof detail === 'object' && detail !== null) {
    return Object.entries(detail)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
      .join('；')
  }
  return error?.message ?? '请求失败'
}

export default client
