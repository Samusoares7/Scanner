<template>
  <div class="page">
    <div class="topbar">
      <div>
        <h1 class="page-title">Alvos</h1>
        <span class="page-sub">Histórico de alvos escaneados</span>
      </div>
    </div>

    <div class="targets-grid" v-if="targets.length > 0">
      <div v-for="target in targets" :key="target.name" class="target-card">
        <div class="target-header">
          <div class="target-name">{{ target.name }}</div>
          <span class="badge-risk" :class="target.topRisk.toLowerCase()">
            ● {{ target.topRisk }}
          </span>
        </div>
        <div class="target-stats">
          <div class="tstat">
            <span class="tstat-val">{{ target.totalScans }}</span>
            <span class="tstat-lbl">Scans</span>
          </div>
          <div class="tstat">
            <span class="tstat-val">{{ target.totalPorts }}</span>
            <span class="tstat-lbl">Portas</span>
          </div>
          <div class="tstat">
            <span class="tstat-val critical">{{ target.critical }}</span>
            <span class="tstat-lbl">Críticos</span>
          </div>
        </div>
        <div class="target-last">Último scan: {{ target.lastScan }}</div>
        <router-link to="/scanner" class="btn-rescan">🔍 Novo Scan</router-link>
      </div>
    </div>

    <div class="empty-panel" v-else>
      <div class="empty-icon">🎯</div>
      <div class="empty-title">Nenhum alvo registrado</div>
      <div class="empty-sub">Inicie uma varredura para ver os alvos aqui.</div>
      <router-link to="/scanner" class="btn-start">Iniciar Scanner →</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getScans } from '../services/api'

const targets = ref([])

onMounted(async () => {
  try {
    const response = await getScans()
    const scans = response.data
    const map = {}
    scans.forEach(scan => {
      if (!map[scan.target]) {
        map[scan.target] = { name: scan.target, totalScans: 0, totalPorts: 0, critical: 0, attention: 0, lastScan: '', topRisk: 'COMMON' }
      }
      const t = map[scan.target]
      t.totalScans++
      t.totalPorts += scan.total_open_ports
      scan.results.forEach(r => {
        if (r.risk === 'CRITICAL') t.critical++
        else if (r.risk === 'ATTENTION') t.attention++
      })
      t.lastScan = new Date(scan.created_at).toLocaleDateString('pt-BR')
      if (t.critical > 0) t.topRisk = 'CRITICAL'
      else if (t.attention > 0) t.topRisk = 'ATTENTION'
    })
    targets.value = Object.values(map)
  } catch (e) {}
})
</script>

<style scoped>
.page { padding: 32px; }
.topbar { margin-bottom: 32px; }
.page-title { font-size: 1.6rem; font-weight: 700; }
.page-sub { font-size: 0.85rem; color: var(--text-secondary); }
.targets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.target-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex; flex-direction: column; gap: 16px;
}
.target-header { display: flex; justify-content: space-between; align-items: flex-start; }
.target-name { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); font-size: 0.9rem; font-weight: 600; word-break: break-all; }
.badge-risk { padding: 4px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; border: 1px solid; }
.badge-risk.critical { color: var(--critical); border-color: var(--critical); background: #ef444415; }
.badge-risk.attention { color: var(--attention); border-color: var(--attention); background: #f59e0b15; }
.badge-risk.common { color: var(--common); border-color: var(--common); background: #10b98115; }
.target-stats { display: flex; gap: 16px; }
.tstat { display: flex; flex-direction: column; gap: 2px; }
.tstat-val { font-size: 1.3rem; font-weight: 700; }
.tstat-val.critical { color: var(--critical); }
.tstat-lbl { font-size: 0.72rem; color: var(--text-secondary); }
.target-last { font-size: 0.78rem; color: var(--text-secondary); }
.btn-rescan {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.82rem;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
  transition: border-color 0.2s;
}
.btn-rescan:hover { border-color: var(--accent-blue); color: var(--accent-blue); }
.empty-panel { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 60px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.empty-icon { font-size: 3rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; }
.empty-sub { color: var(--text-secondary); font-size: 0.85rem; }
.btn-start { padding: 10px 20px; background: var(--accent-blue); border: none; border-radius: 8px; color: white; font-size: 0.85rem; cursor: pointer; text-decoration: none; margin-top: 8px; }
</style>
