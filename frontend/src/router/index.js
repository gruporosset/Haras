import { defineRouter } from '#q-app/wrappers'
import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from '../stores/auth'

export default defineRouter(function () {
  const Router = createRouter({
    routes,
    history: createWebHistory(),
  })

  // Inicializar authStore com tokens do localStorage
  const authStore = useAuthStore()
  const access_token = localStorage.getItem('access_token_haras')
  const refresh_token = localStorage.getItem('refresh_token_haras')
  const user_haras = localStorage.getItem('user_haras')

  if (access_token && refresh_token && user_haras && !authStore.access_token) {
    authStore.setAuthData({
      user: JSON.parse(user_haras),
      access_token: access_token,
      refresh_token: refresh_token,
    })
  }

  Router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth && !authStore.access_token) {
      next('/login')
    } else {
      next()
    }
  })

  return Router
})
