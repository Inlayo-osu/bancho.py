<template>
  <div class="home-page">
    <div class="hero">
      <div class="hero-content">
        <div class="hero-logo">
          <div class="navbar-logo-img"></div>
        </div>
        
        <h1 class="hero-title animate-fadeIn">
          Welcome to Inlayo
        </h1>
        
        <p class="hero-subtitle animate-fadeIn">
          The osu! private server with vanilla, autopilot & relax modes
          <br />
          Join our <a href="/discord" class="hero-link">Discord</a> for the latest updates!
        </p>
        
        <div v-if="!isAuthenticated" class="hero-actions animate-fadeIn">
          <a class="btn btn-primary btn-large" href="/register">
            <i class="fa-solid fa-user-plus"></i>
            Sign up
          </a>
          <a class="btn btn-secondary btn-large" href="/login">
            <i class="fa-solid fa-sign-in-alt"></i>
            Log in
          </a>
        </div>
        
        <div class="hero-stats animate-fadeIn">
          <div class="stat-card">
            <div class="stat-card-value text-success">
              {{ stats.online_users }}
            </div>
            <div class="stat-card-label">Players Online</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-card-value text-primary-pink">
              {{ stats.registered_users }}
            </div>
            <div class="stat-card-label">Total Players</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { apiClient } from '@/api/client'

const sessionStore = useSessionStore()
const isAuthenticated = computed(() => sessionStore.isAuthenticated)

const stats = ref({
  online_users: 0,
  registered_users: 0
})

async function loadStats() {
  try {
    const data = await apiClient.get<any>('/v1/get_stats')
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  sessionStore.loadFromGlobal()
  loadStats()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.hero {
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
  text-align: center;
}

.hero-logo {
  margin-bottom: 2rem;
}

.navbar-logo-img {
  width: 350px;
  height: 110px;
  margin: 0 auto;
  background: url('/static/images/logo.png') center/contain no-repeat;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--primary) 0%, #ff66aa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.hero-link {
  color: #ff66aa;
  font-weight: 600;
}

.hero-link:hover {
  text-decoration: underline;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all var(--transition-base);
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 136, 204, 0.4);
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
  transform: translateY(-2px);
}

.btn-large {
  font-size: 1.125rem;
  padding: 1.25rem 2.5rem;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  max-width: 600px;
  margin: 0 auto;
}

.stat-card {
  background: rgba(45, 45, 66, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 2rem 1rem;
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(45, 45, 66, 0.8);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.stat-card-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-card-label {
  color: var(--text-muted);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.text-success {
  color: #68d57f;
}

.text-primary-pink {
  color: #ff66aa;
}

.animate-fadeIn {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
