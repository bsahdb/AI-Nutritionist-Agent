import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../views/Dashboard.vue'
import HealthReport from '../views/HealthReport.vue'
import Preferences from '../views/Preferences.vue'
import MealPlan from '../views/MealPlan.vue'
import MealPlanDetail from '../views/MealPlanDetail.vue'
import Chat from '../views/Chat.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
  path: '/users',
  component: () => import('@/views/UserManage.vue')
  },
  {
    path: '/health',
    name: 'HealthReport',
    component: HealthReport
  },
  {
    path: '/preferences',
    name: 'Preferences',
    component: Preferences
  },
  {
    path: '/meal-plan',
    name: 'MealPlan',
    component: MealPlan
  },
  {
    path: '/meal-plan/detail/:planId',
    name: 'MealPlanDetail',
    component: MealPlanDetail
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router