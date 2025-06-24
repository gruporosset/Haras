import LoginPage from '../pages/LoginPage.vue'
import ForgotPasswordPage from '../pages/ForgotPasswordPage.vue'
import ResetPasswordPage from '../pages/ResetPasswordPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import TerrenosPage from '../pages/TerrenosPage.vue'
import AnimaisPage from '../pages/AnimaisPage.vue'
// import CrescimentoSaudePage from '../pages/CrescimentoSaudePage.vue'
import CrescimentoPage from '../pages/CrescimentoPage.vue'
import CrescimentoAnimalPage from '../pages/CrescimentoAnimalPage.vue'
import MovimentacoesPage from '../pages/MovimentacoesPage.vue'
import ReproducaoPage from '../pages/ReproducaoPage.vue'
import ManejoPage from '../pages/ManejoPage.vue'
import MedicamentosPage from '../pages/MedicamentosPage.vue'
import SaudePage from 'pages/SaudePage.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false },
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
    meta: { requiresAuth: true },
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
    path: '/crescimento',
    name: 'Crescimento',
    component: CrescimentoPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/crescimento/animal/:id',
    name: 'CrescimentoAnimal',
    component: CrescimentoAnimalPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/movimentacoes',
    name: 'Movimentacoes',
    component: MovimentacoesPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/reproducao',
    name: 'Reproducao',
    component: ReproducaoPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/manejo',
    name: 'Manejo',
    component: ManejoPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/medicamentos',
    name: 'Medicamentos',
    component: MedicamentosPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/saude',
    name: 'saude',
    component: SaudePage,
    meta: {
      requiresAuth: true,
    },
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
