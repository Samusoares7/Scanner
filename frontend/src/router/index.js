import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ScannerView from '../views/ScannerView.vue'
import AlvosView from '../views/AlvosView.vue'
import RelatoriosView from '../views/RelatoriosView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/', redirect: '/dashboard' },
    { path: '/scanner', component: ScannerView, meta: { requiresAuth: true } },
    { path: '/alvos', component: AlvosView, meta: { requiresAuth: true } },
    { path: '/relatorios', component: RelatoriosView, meta: { requiresAuth: true } }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
