<template>
  <div class="profile-page" :class="{ load: loading }">
    <!-- Profile Header -->
    <div class="profile-header" v-if="userData">
      <div class="profile-banner">
        <div class="profile-info">
          <div class="profile-avatar">
            <img :src="`https://a.${domain}/${userData.user.id}`" :alt="userData.user.name" />
          </div>
          <div class="profile-details">
            <h1 class="profile-name">
              <img :src="`/static/images/flags/${userData.user.country}.png`" class="flag" />
              {{ userData.user.name }}
            </h1>
            <div class="profile-status">
              <span :class="['status-indicator', userData.status.online ? 'online' : 'offline']">●</span>
              {{ userData.status.online ? 'Online' : 'Offline' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mode Selector -->
    <div class="mode-selector">
      <button
        v-for="mode in modes"
        :key="mode.id"
        :class="['mode-btn', { active: currentMode === mode.id }]"
        @click="changeMode(mode.id)"
      >
        <i :class="['fas', mode.icon]" :style="{ color: mode.color }"></i>
        {{ mode.name }}
      </button>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid" v-if="currentStats">
      <div class="stat-card">
        <div class="stat-label">Global Rank</div>
        <div class="stat-value">#{{ formatNumber(currentStats.rank) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Country Rank</div>
        <div class="stat-value">#{{ formatNumber(currentStats.country_rank) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Performance</div>
        <div class="stat-value">{{ formatNumber(Math.round(currentStats.pp)) }}pp</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Accuracy</div>
        <div class="stat-value">{{ currentStats.acc.toFixed(2) }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Play Count</div>
        <div class="stat-value">{{ formatNumber(currentStats.plays) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Playtime</div>
        <div class="stat-value">{{ formatPlaytime(currentStats.playtime) }}</div>
      </div>
    </div>

    <!-- Scores Section -->
    <div class="scores-section">
      <ScoreList
        title="Best Performance"
        :scores="userData?.best_scores || []"
        :loading="loading"
      />
      <ScoreList
        title="Recent Plays"
        :scores="userData?.recent_scores || []"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { userApi } from '@/api/users'
import { useGameMode } from '@/composables/useGameMode'
import { formatNumber, formatPlaytime } from '@/utils/format'
import type { UserProfileData } from '@/api/users'
import ScoreList from './ScoreList.vue'

const props = defineProps<{
  userId: number
  initialMode?: number
}>()

const domain = ref(window.location.hostname)
const loading = ref(true)
const userData = ref<UserProfileData | null>(null)
const { currentMode, getModeInfo, setMode } = useGameMode()

const modes = [
  { id: 0, name: 'osu!', icon: 'fa-circle', color: '#ff66aa' },
  { id: 1, name: 'taiko', icon: 'fa-drum', color: '#ff8c1a' },
  { id: 2, name: 'catch', icon: 'fa-apple-alt', color: '#66cc66' },
  { id: 3, name: 'mania', icon: 'fa-th', color: '#a366ff' }
]

const currentStats = computed(() => {
  if (!userData.value) return null
  return userData.value.stats[currentMode.value.toString()]
})

async function loadProfile() {
  loading.value = true
  try {
    userData.value = await userApi.getProfile(props.userId, currentMode.value, 0)
  } catch (error) {
    console.error('Failed to load profile:', error)
  } finally {
    loading.value = false
  }
}

function changeMode(mode: number) {
  setMode(mode)
  loadProfile()
}

onMounted(() => {
  if (props.initialMode !== undefined) {
    setMode(props.initialMode)
  }
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.profile-banner {
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  border-radius: var(--radius-lg);
  padding: 2rem;
  margin-bottom: 2rem;
}

.profile-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid var(--primary);
}

.profile-name {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.flag {
  width: 32px;
  height: 24px;
  border-radius: 4px;
}

.profile-status {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  font-size: 1.2rem;
}

.status-indicator.online {
  color: var(--success);
}

.status-indicator.offline {
  color: var(--text-muted);
}

.mode-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.mode-btn {
  padding: 0.75rem 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mode-btn:hover {
  background: var(--bg-tertiary);
  transform: translateY(-2px);
}

.mode-btn.active {
  background: var(--primary);
  border-color: var(--primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  text-align: center;
}

.stat-label {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
}

.scores-section {
  display: grid;
  gap: 2rem;
}

@media (max-width: 768px) {
  .profile-info {
    flex-direction: column;
    text-align: center;
  }

  .profile-name {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
