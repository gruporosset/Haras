import LoginPage from "../pages/LoginPage.vue"
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue';
import ResetPasswordPage from '../pages/ResetPasswordPage.vue';
import DashboardPage from "../pages/DashboardPage.vue"
import ProfilePage from '../pages/ProfilePage.vue';
import TerrenosPage from '../pages/TerrenosPage.vue'
import AnimaisPage from '../pages/AnimaisPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordPage,
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPasswordPage,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/terrenos',
    name: 'Terrenos',
    component: TerrenosPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/animais',
    name: 'Animais',
    component: AnimaisPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes