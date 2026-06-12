<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">🛡️</div>
      <div class="logo-text">
        <span class="logo-name">Scanner-Pro</span>
        <span class="logo-sub">Security Operations Center</span>
      </div>
    </div>

    <!-- Navegação -->
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item">
        <span class="nav-icon">📊</span>
        <span>Dashboard</span>
      </router-link>
      <router-link to="/scanner" class="nav-item">
        <span class="nav-icon">🔍</span>
        <span>Scanner</span>
      </router-link>
      <router-link to="/alvos" class="nav-item">
        <span class="nav-icon">🎯</span>
        <span>Alvos</span>
      </router-link>
      <router-link to="/relatorios" class="nav-item">
        <span class="nav-icon">📄</span>
        <span>Relatórios</span>
      </router-link>
    </nav>

    <!-- Card do operador -->
    <div class="operator-card">
      <div class="operator-avatar">A</div>
      <div class="operator-info">
        <span class="operator-name">Admin</span>
        <span class="operator-status">
          <span class="status-dot"></span>
          Online
        </span>
      </div>
      <button class="logout-btn" @click="logout" title="Sair">⏻</button>
    </div>

    <!-- Distribuição de risco -->
    <div class="risk-distribution" v-if="stats">
      <div class="risk-title">DISTRIBUIÇÃO DE RISCO</div>
      <div class="risk-item">
        <span class="risk-label">CRITICAL</span>
        <div class="risk-bar-track">
          <div class="risk-bar-fill critical" :style="{ width: stats.pctCritical }"></div>
        </div>
        <span class="risk-pct">{{ stats.pctCritical }}</span>
      </div>
      <div class="risk-item">
        <span class="risk-label">ATTENTION</span>
        <div class="risk-bar-track">
          <div class="risk-bar-fill attention" :style="{ width: stats.pctAttention }"></div>
        </div>
        <span class="risk-pct">{{ stats.pctAttention }}</span>
      </div>
      <div class="risk-item">
        <span class="risk-label">COMMON</span>
        <div class="risk-bar-track">
          <div class="risk-bar-fill common" :style="{ width: stats.pctCommon }"></div>
        </div>
        <span class="risk-pct">{{ stats.pctCommon }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({ stats: Object })
const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  min-height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  gap: 8px;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.logo-icon { font-size: 1.8rem; }
.logo-text { display: flex; flex-direction: column; }
.logo-name { font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.logo-sub { font-size: 0.65rem; color: var(--text-secondary); letter-spacing: 0.05em; }
.sidebar-nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.router-link-active {
  background: var(--accent-blue);
  color: white;
}
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }
.operator-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  border: 1px solid var(--border);
  margin-top: 8px;
}
.operator-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: white;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.operator-info { display: flex; flex-direction: column; flex: 1; }
.operator-name { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); }
.operator-status { display: flex; align-items: center; gap: 4px; font-size: 0.75rem; color: var(--common); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--common); }
.logout-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}
.logout-btn:hover { color: var(--critical); }
.risk-distribution {
  margin-top: 16px;
  padding: 16px 12px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  border: 1px solid var(--border);
}
.risk-title {
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-weight: 600;
}
.risk-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.risk-label { font-size: 0.7rem; color: var(--text-secondary); width: 65px; }
.risk-bar-track { flex: 1; height: 4px; background: var(--border); border-radius: 2px; }
.risk-bar-fill { height: 4px; border-radius: 2px; transition: width 0.5s; }
.risk-bar-fill.critical { background: var(--critical); }
.risk-bar-fill.attention { background: var(--attention); }
.risk-bar-fill.common { background: var(--common); }
.risk-pct { font-size: 0.7rem; color: var(--text-secondary); width: 30px; text-align: right; }
</style>
