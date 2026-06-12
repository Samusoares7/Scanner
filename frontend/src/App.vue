<template>
  <div id="app">
    <div v-if="isAuthenticated" class="app-layout">
      <Sidebar :stats="globalStats" />
      <main class="app-main">
        <RouterView @stats-updated="updateStats" />
      </main>
    </div>
    <RouterView v-else />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const globalStats = ref(null)

const isAuthenticated = computed(() => {
  const publicRoutes = ['/login']
  return !publicRoutes.includes(route.path) && !!localStorage.getItem('token')
})

const updateStats = (stats) => {
  globalStats.value = stats
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-primary:     #0a0e1a;
  --bg-secondary:   #0f1629;
  --bg-tertiary:    #141d35;
  --border:         #1e2d4a;
  --accent-blue:    #2563eb;
  --accent-cyan:    #06b6d4;
  --critical:       #ef4444;
  --attention:      #f59e0b;
  --common:         #10b981;
  --text-primary:   #e2e8f0;
  --text-secondary: #64748b;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  line-height: 1.5;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  margin-left: 260px;
  flex: 1;
  min-height: 100vh;
  background: var(--bg-primary);
  overflow-y: auto;
}
</style>
