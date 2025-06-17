import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'
import api from './api' // Importa a instância configurada

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})