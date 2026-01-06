import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import global styles
import './styles/main.css'

// Create Vue app
const app = createApp(App)

// Use Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Mount app
app.mount('#app')

// Export for global access
export { app, pinia }
