import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api'

function isSuccess(res: any) {
  return res?.success === true || res?.code === 200
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<any>(null)
  const preferences = ref<any>(null)
  const loading = ref(false)

  const demoUserId = 1

  const isLoggedIn = computed(() => true)

  const userId = computed(() => {
    return currentUser.value?.id || Number(localStorage.getItem('nutritionist_user_id')) || demoUserId
  })

  const bmi = computed(() => currentUser.value?.bmi || 0)

  async function init() {
    const savedUserId = Number(localStorage.getItem('nutritionist_user_id')) || demoUserId
    await fetchUser(savedUserId)
  }

  async function fetchUser(uid: number) {
    loading.value = true

    try {
      const res = await api.getUser(uid)

      if (isSuccess(res)) {
        currentUser.value = res.data
        localStorage.setItem('nutritionist_user_id', String(uid))
        await fetchPreferences(uid)
      }
    } catch (error) {
      console.error('获取用户失败：', error)

      currentUser.value = {
        id: demoUserId,
        username: 'demo_user'
      }

      localStorage.setItem('nutritionist_user_id', String(demoUserId))
    } finally {
      loading.value = false
    }
  }

  async function setCurrentUser(user: any) {
    currentUser.value = user
    localStorage.setItem('nutritionist_user_id', String(user.id))
    await fetchPreferences(user.id)
  }

  async function createUser(data: any) {
    loading.value = true

    try {
      const res = await api.createUser(data)

      if (isSuccess(res)) {
        await setCurrentUser(res.data)
        return res.data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchPreferences(uid: number) {
    try {
      const res = await api.getPreferences(uid)

      if (isSuccess(res)) {
        preferences.value = res.data
      }
    } catch (error: any) {
      if (error?.response?.status === 404) {
        preferences.value = null
      } else {
        console.error('获取口味偏好失败：', error)
      }
    }
  }

  async function saveUserPreferences(data: any) {
    const uid = userId.value
    const res = await api.savePreferences(uid, data)

    if (isSuccess(res)) {
      await fetchPreferences(uid)
      return res.data
    }
  }

  function logout() {
    currentUser.value = {
      id: demoUserId,
      username: 'demo_user'
    }

    preferences.value = null
    localStorage.setItem('nutritionist_user_id', String(demoUserId))
  }

  return {
    currentUser,
    preferences,
    loading,
    isLoggedIn,
    userId,
    bmi,
    init,
    fetchUser,
    setCurrentUser,
    createUser,
    fetchPreferences,
    saveUserPreferences,
    logout
  }
})