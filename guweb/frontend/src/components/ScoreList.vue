<template>
  <div class="score-list">
    <h2 class="score-list-title">
      <i class="fas fa-trophy"></i>
      {{ title }}
    </h2>

    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> Loading...
    </div>

    <div v-else-if="scores.length === 0" class="empty-state">
      <i class="fas fa-inbox"></i>
      <p>No scores yet</p>
    </div>

    <div v-else class="scores">
      <div v-for="score in scores" :key="score.id" class="score-card">
        <div class="score-beatmap">
          <div class="beatmap-cover">
            <img :src="`https://assets.ppy.sh/beatmaps/${score.beatmap_md5}/covers/card.jpg`" />
          </div>
          <div class="beatmap-info">
            <a :href="`/scores/${score.id}`" class="beatmap-title">
              {{ score.beatmap?.title }} [{{ score.beatmap?.version }}]
            </a>
            <div class="beatmap-artist">{{ score.beatmap?.artist }}</div>
            <div class="score-time">{{ formatTime(score.play_time) }}</div>
          </div>
        </div>

        <div class="score-details">
          <div class="score-mods" v-if="score.mods">
            <span class="mod-badge">+{{ getModsString(score.mods) }}</span>
          </div>
          <div class="score-pp">{{ Math.round(score.pp) }}pp</div>
          <div class="score-acc">{{ score.acc.toFixed(2) }}%</div>
          <div class="score-grade">
            <span :class="['grade-badge', getGradeClass(score.grade)]">
              {{ score.grade }}
            </span>
          </div>
        </div>

        <div class="score-stats">
          <span class="stat-hit good">{{ score.n300 }} ⬤</span>
          <span class="stat-hit ok">{{ score.n100 }} ⬤</span>
          <span class="stat-hit miss">{{ score.nmiss }} ⬤</span>
          <span class="combo">{{ score.max_combo }}x</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Score } from '@/types'
import { getModsString } from '@/utils/mods'
import { getGradeClass } from '@/utils/grade'
import { format as formatTime } from 'timeago.js'

defineProps<{
  title: string
  scores: Score[]
  loading?: boolean
}>()
</script>

<style scoped>
.score-list {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
}

.score-list-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-size: 1.25rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.scores {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1rem;
  align-items: center;
  transition: all var(--transition-base);
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.score-beatmap {
  display: flex;
  gap: 1rem;
  align-items: center;
  min-width: 0;
}

.beatmap-cover {
  flex-shrink: 0;
  width: 80px;
  height: 60px;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.beatmap-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.beatmap-info {
  min-width: 0;
}

.beatmap-title {
  color: var(--text-primary);
  font-weight: 600;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.beatmap-artist {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.score-time {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.score-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.score-pp {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
}

.score-acc {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.mod-badge {
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.grade-badge {
  display: inline-block;
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1.1rem;
}

.grade-badge.rank-xh,
.grade-badge.rank-sh {
  background: #d4d4d4;
  color: #333;
}

.grade-badge.rank-x,
.grade-badge.rank-s {
  background: #ffdd55;
  color: #333;
}

.grade-badge.rank-a {
  background: #88da20;
  color: white;
}

.grade-badge.rank-b {
  background: #4a9beb;
  color: white;
}

.score-stats {
  display: flex;
  gap: 0.75rem;
  font-size: 0.875rem;
}

.stat-hit.good {
  color: rgb(172, 235, 140);
}

.stat-hit.ok {
  color: rgb(232, 213, 167);
}

.stat-hit.miss {
  color: rgb(254, 179, 179);
}

.combo {
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .score-card {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .score-details {
    align-items: flex-start;
  }
}
</style>
