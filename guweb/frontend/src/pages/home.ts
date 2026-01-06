import { createApp } from 'vue'
import { createPinia } from 'pinia'
import HomePage from '@/components/HomePage.vue'

const app = createApp(HomePage)
const pinia = createPinia()

app.use(pinia)
app.mount('#home-app')
