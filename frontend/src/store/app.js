import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchTestApi } from '../api/test'

export const useAppStore = defineStore('app', () => {
  const apiStatus = ref('idle')
  const apiMessage = ref('')
  const apiError = ref('')

  async function loadTestApi() {
    apiStatus.value = 'loading'
    apiError.value = ''
    try {
      const { data } = await fetchTestApi()
      apiStatus.value = data.status
      apiMessage.value = data.message
    } catch (error) {
      apiStatus.value = 'error'
      apiMessage.value = ''
      apiError.value = error?.message ?? 'Request failed'
    }
  }

  return {
    apiStatus,
    apiMessage,
    apiError,
    loadTestApi,
  }
})
