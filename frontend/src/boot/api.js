import axios from 'axios'
import { Loading } from 'quasar'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  },  
  withCredentials: true,
})

api.interceptors.request.use(
  (config) => {
    Loading.show()
    const authStore = useAuthStore()
    if (authStore.access_token) {
      config.headers.Authorization = `Bearer ${authStore.access_token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    Loading.hide()
    return response
  },
  async (error) => {
    Loading.show()
    const authStore = useAuthStore()
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        await authStore.refreshToken()
        originalRequest.headers.Authorization = `Bearer ${authStore.access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        authStore.clearAuthData()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    Loading.hide()
    return Promise.reject(error)
  }
)


export default api