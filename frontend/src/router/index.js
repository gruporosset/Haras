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
    const token_haras = localStorage.getItem('token_haras');
    if (!authStore.token && token_haras) {
        const user_haras = localStorage.getItem('user_haras');
        authStore.setAuthData({
          user: JSON.parse(user_haras),
          token: token_haras
        });
    }    
    
    if (to.meta.requiresAuth && !authStore.token) {
      next('/login');
    } else {
      next();
    } 
 })

  return Router
})