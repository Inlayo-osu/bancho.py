import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ProfilePage from '@/components/ProfilePage.vue'

// Get user ID from URL or data attribute
const userId = parseInt(document.getElementById('profile-app')?.dataset.userId || '0')
const initialMode = parseInt(document.getElementById('profile-app')?.dataset.mode || '0')

if (userId) {
  const app = createApp(ProfilePage, {
    userId,
    initialMode
  })

  const pinia = createPinia()
  app.use(pinia)

  app.mount('#profile-app')
}
