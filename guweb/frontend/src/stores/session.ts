import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session } from '@/types'

export const useSessionStore = defineStore('session', () => {
  const session = ref<Session>({
    authenticated: false
  })

  const isAuthenticated = computed(() => session.value.authenticated)
  const currentUser = computed(() => session.value.user_data)
  const userId = computed(() => session.value.user_data?.id)

  function setSession(sessionData: Session) {
    session.value = sessionData
  }

  function clearSession() {
    session.value = {
      authenticated: false
    }
  }

  // Load session from window global (set by Jinja2 template)
  function loadFromGlobal() {
    if (typeof window !== 'undefined' && (window as any).session) {
      session.value = (window as any).session
    }
  }

  return {
    session,
    isAuthenticated,
    currentUser,
    userId,
    setSession,
    clearSession,
    loadFromGlobal
  }
})
