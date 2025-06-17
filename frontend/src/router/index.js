import { defineRouter } from '#q-app/wrappers'
import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from '../stores/auth'

export default defineRouter(function () {
  const Router = createRouter({
    routes,
    history: createWebHistory(),
  })

  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    
    if (to.meta.requiresAuth && !authStore.token) {
      next('/login');
    } else {
      next();
    } 
 })

  return Router
})