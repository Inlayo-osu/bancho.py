<template>
  <div id="app" class="app">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()

onMounted(() => {
  // Load session from global window object
  sessionStore.loadFromGlobal()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
