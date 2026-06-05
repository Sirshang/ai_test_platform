import client from './client'

export function fetchTestApi() {
  return client.get('/test/')
}
