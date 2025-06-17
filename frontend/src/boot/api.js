import axios from 'axios'
import { Loading } from 'quasar'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

// Adicione seus interceptors aqui
api.interceptors.request.use(config => {
  Loading.show()
  return config
})

api.interceptors.response.use(
  response => {
    Loading.hide()
    return response
  },
  error => {
    Loading.hide()
    return Promise.reject(error)
  }
)

export default api