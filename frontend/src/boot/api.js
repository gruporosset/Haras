import axios from 'axios'
import { Loading } from 'quasar'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

api.interceptors.request.use(config => {
  Loading.show()
  const token = localStorage.getItem('token_haras');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }  
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