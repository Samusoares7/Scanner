<template>
  <div class="page">
    <!-- Top Bar -->
    <div class="topbar">
      <div class="topbar-left">
        <h1 class="page-title">Dashboard</h1>
        <span class="page-sub">Visão geral da segurança</span>
      </div>
      <div class="topbar-right">
        <button class="btn-export" @click="exportPDF" :disabled="exporting">
          {{ exporting ? 'Gerando...' : '📄 Exportar PDF' }}
        </button>
      </div>
    </div>

    <!-- Métricas -->
    <div class="metrics">
      <div class="metric-card">
        <div class="metric-icon blue">📊</div>
        <div class="metric-info">
          <span class="metric-value">{{ stats.totalScans }}</span>
          <span class="metric-label">Total de Scans</span>
        </div>
        <span class="metric-update">• atualizado agora</span>
      </div>
      <div class="metric-card">
        <div class="metric-icon cyan">🎯</div>
        <div class="metric-info">
          <span class="metric-value">{{ stats.uniqueTargets }}</span>
          <span class="metric-label">Alvos Únicos</span>
        </div>
        <span class="metric-update">• atualizado agora</span>
      </div>
      <div class="metric-card">
        <div class="metric-icon red">⚠️</div>
        <div class="metric-info">
          <span class="metric-value critical">{{ stats.critical }}</span>
          <span class="metric-label">Críticas</span>
        </div>
        <span class="metric-update critical-dot">• atualizado agora</span>
      </div>
      <div class="metric-card">
        <div class="metric-icon yellow">🔔</div>
        <div class="metric-info">
          <span class="metric-value attention">{{ stats.attention }}</span>
          <span class="metric-label">Atenção</span>
        </div>
        <span class="metric-update">• atualizado agora</span>
      </div>
      <div class="metric-card">
        <div class="metric-icon green">✅</div>
        <div class="metric-info">
          <span class="metric-value common">{{ stats.common }}</span>
          <span class="metric-label">Comuns</span>
        </div>
        <span class="metric-update">• atualizado agora</span>
      </div>
    </div>

    <!-- Histórico -->
    <div class="section">
      <div class="section-header">
        <div>
          <h2>Histórico de Scans por Alvo</h2>
          <p class="section-sub">Acompanhe as varreduras realizadas e seus resultados.</p>
        </div>
        <div class="section-actions">
          <router-link to="/scanner" class="btn-new">+ Novo</router-link>
          <button class="btn-clear" @click="confirmClear" :disabled="scans.length === 0">
            🗑 Limpar
          </button>
        </div>
      </div>

      <div v-if="loading" class="empty-state">Carregando...</div>
      <div v-else-if="scans.length === 0" class="empty-state">
        Nenhum scan realizado ainda. <router-link to="/scanner">Iniciar varredura →</router-link>
      </div>

      <div v-else class="scan-list">
        <div v-for="scan in scans" :key="scan.id" class="scan-item">
          <div class="scan-header" @click="toggleScan(scan.id)">
            <div class="scan-left">
              <span class="chevron" :class="{ open: openScans.includes(scan.id) }">›</span>
              <div>
                <div class="scan-target">{{ scan.target }}</div>
                <div class="scan-date">🕐 {{ formatDate(scan.created_at) }}</div>
              </div>
            </div>
            <div class="scan-right">
              <span class="badge-info">{{ scan.total_open_ports }} portas</span>
              <span class="badge-info">{{ scan.total_findings }} findings</span>
              <span class="badge-risk" :class="topRisk(scan.results).toLowerCase()">
                ● {{ topRisk(scan.results) }}
              </span>
            </div>
          </div>

          <div v-if="openScans.includes(scan.id)" class="scan-body">
            <table>
              <thead>
                <tr>
                  <th>PORTA</th>
                  <th>SERVIÇO</th>
                  <th>RISCO</th>
                  <th>CONTEXTO</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in scan.results" :key="r.port + r.service" :class="r.risk.toLowerCase()">
                  <td class="mono">{{ r.port }}</td>
                  <td>{{ r.service }}</td>
                  <td>
                    <span class="risk-badge" :class="r.risk.toLowerCase()">{{ r.risk }}</span>
                  </td>
                  <td class="context-cell">{{ r.context || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal confirmação -->
    <div v-if="showConfirm" class="modal-overlay">
      <div class="modal">
        <h3>Limpar Histórico</h3>
        <p>Todos os scans serão apagados permanentemente.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm = false">Cancelar</button>
          <button class="btn-confirm" @click="clearHistory">Confirmar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getScans, downloadReport } from '../services/api'
import axios from 'axios'

const router = useRouter()
const scans = ref([])
const loading = ref(true)
const showConfirm = ref(false)
const exporting = ref(false)
const openScans = ref([])

const emit = defineEmits(['stats-updated'])

onMounted(async () => {
  await loadScans()
})

const loadScans = async () => {
  loading.value = true
  try {
    const response = await getScans()
    scans.value = response.data
    emit('stats-updated', stats.value)
  } catch (e) {
    router.push('/login')
  } finally {
    loading.value = false
  }
}

const stats = computed(() => {
  let critical = 0, attention = 0, common = 0
  const targets = new Set()
  scans.value.forEach(scan => {
    targets.add(scan.target)
    scan.results.forEach(r => {
      if (r.risk === 'CRITICAL') critical++
      else if (r.risk === 'ATTENTION') attention++
      else common++
    })
  })
  const total = critical + attention + common
  return {
    totalScans: scans.value.length,
    uniqueTargets: targets.size,
    critical, attention, common,
    pctCritical: total ? Math.round(critical/total*100) + '%' : '0%',
    pctAttention: total ? Math.round(attention/total*100) + '%' : '0%',
    pctCommon: total ? Math.round(common/total*100) + '%' : '0%',
  }
})

const toggleScan = (id) => {
  const idx = openScans.value.indexOf(id)
  if (idx === -1) openScans.value.push(id)
  else openScans.value.splice(idx, 1)
}

const topRisk = (results) => {
  if (!results?.length) return 'COMMON'
  if (results.some(r => r.risk === 'CRITICAL')) return 'CRITICAL'
  if (results.some(r => r.risk === 'ATTENTION')) return 'ATTENTION'
  return 'COMMON'
}

const formatDate = (dt) => new Date(dt).toLocaleDateString('pt-BR', {
  day: '2-digit', month: '2-digit', year: 'numeric',
  hour: '2-digit', minute: '2-digit'
})

const confirmClear = () => { showConfirm.value = true }

const clearHistory = async () => {
  try {
    const token = localStorage.getItem('token')
    await axios.delete('https://scanner-pro-ti44.onrender.com/scans', {
      headers: { Authorization: `Bearer ${token}` }
    })
    scans.value = []
    showConfirm.value = false
    emit('stats-updated', stats.value)
  } catch (e) {
    alert('Erro ao limpar histórico')
  }
}

const exportPDF = async () => {
  exporting.value = true
  try {
    const response = await downloadReport()
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'scanner-pro-report.pdf')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (e) {
    alert('Erro ao gerar relatório')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.page { padding: 32px; max-width: 1100px; }
.topbar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; }
.page-title { font-size: 1.6rem; font-weight: 700; }
.page-sub { font-size: 0.85rem; color: var(--text-secondary); }
.btn-export {
  padding: 10px 20px;
  background: var(--accent-blue);
  border: none; border-radius: 8px;
  color: white; font-size: 0.85rem;
  cursor: pointer; font-weight: 500;
}
.btn-export:disabled { opacity: 0.5; cursor: not-allowed; }

/* Métricas */
.metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 32px; }
.metric-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}
.metric-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.metric-icon.blue { background: #2563eb20; }
.metric-icon.cyan { background: #06b6d420; }
.metric-icon.red { background: #ef444420; }
.metric-icon.yellow { background: #f59e0b20; }
.metric-icon.green { background: #10b98120; }
.metric-info { display: flex; flex-direction: column; gap: 2px; }
.metric-value { font-size: 2rem; font-weight: 700; }
.metric-value.critical { color: var(--critical); }
.metric-value.attention { color: var(--attention); }
.metric-value.common { color: var(--common); }
.metric-label { font-size: 0.8rem; color: var(--text-secondary); }
.metric-update { font-size: 0.7rem; color: var(--text-secondary); }
.metric-update.critical-dot { color: var(--critical); }

/* Section */
.section { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.section-header h2 { font-size: 1rem; font-weight: 600; margin-bottom: 4px; }
.section-sub { font-size: 0.8rem; color: var(--text-secondary); }
.section-actions { display: flex; gap: 8px; }
.btn-new {
  padding: 8px 16px;
  background: var(--accent-blue);
  border: none; border-radius: 8px;
  color: white; font-size: 0.8;
  cursor: pointer; text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
}
.btn-clear {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--critical);
  border-radius: 8px;
  color: var(--critical);
  font-size: 0.8rem; cursor: pointer;
}
.btn-clear:disabled { opacity: 0.4; cursor: not-allowed; }
.empty-state { text-align: center; padding: 48px; color: var(--text-secondary); }
.empty-state a { color: var(--accent-cyan); text-decoration: none; }

/* Scan list */
.scan-list { display: flex; flex-direction: column; gap: 8px; }
.scan-item { background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.scan-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; cursor: pointer;
  transition: background 0.2s;
}
.scan-header:hover { background: #1e2d4a30; }
.scan-left { display: flex; align-items: center; gap: 12px; }
.chevron { font-size: 1.2rem; color: var(--text-secondary); transition: transform 0.2s; display: inline-block; }
.chevron.open { transform: rotate(90deg); }
.scan-target { font-size: 0.95rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); }
.scan-date { font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px; }
.scan-right { display: flex; align-items: center; gap: 8px; }
.badge-info {
  padding: 4px 10px; background: var(--bg-secondary);
  border: 1px solid var(--border); border-radius: 20px;
  font-size: 0.75rem; color: var(--text-secondary);
}
.badge-risk {
  padding: 4px 12px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600; border: 1px solid;
}
.badge-risk.critical { color: var(--critical); border-color: var(--critical); background: #ef444415; }
.badge-risk.attention { color: var(--attention); border-color: var(--attention); background: #f59e0b15; }
.badge-risk.common { color: var(--common); border-color: var(--common); background: #10b98115; }

/* Tabela */
.scan-body { border-top: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; }
th { padding: 10px 20px; text-align: left; font-size: 0.7rem; color: var(--text-secondary); letter-spacing: 0.05em; border-bottom: 1px solid var(--border); }
td { padding: 12px 20px; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
tr:last-child td { border-bottom: none; }
.mono { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); }
.risk-badge {
  padding: 3px 8px; border-radius: 4px;
  font-size: 0.75rem; font-weight: 600;
}
.risk-badge.critical { background: #ef444420; color: var(--critical); }
.risk-badge.attention { background: #f59e0b20; color: var(--attention); }
.risk-badge.common { background: #10b98120; color: var(--common); }
.context-cell { color: var(--text-secondary); font-size: 0.82rem; max-width: 300px; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 32px; max-width: 400px; width: 90%; }
.modal h3 { margin-bottom: 8px; }
.modal p { color: var(--text-secondary); margin-bottom: 24px; font-size: 0.9rem; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.btn-cancel { padding: 8px 20px; background: transparent; border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); cursor: pointer; }
.btn-confirm { padding: 8px 20px; background: var(--critical); border: none; border-radius: 8px; color: white; cursor: pointer; }

/* ── Tablet ── */
@media (max-width: 1024px) {
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .context-cell { max-width: 200px; }
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .page { padding: 16px; }
  .topbar { flex-direction: column; gap: 12px; }
  .page-title { font-size: 1.3rem; }
  .metrics { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .metric-card { padding: 14px; }
  .metric-value { font-size: 1.5rem; }
  .section { padding: 16px; }
  .section-header { flex-direction: column; gap: 12px; }
  .section-actions { width: 100%; }
  .btn-new, .btn-clear { flex: 1; justify-content: center; text-align: center; }
  .scan-header { flex-direction: column; align-items: flex-start; gap: 10px; padding: 12px 14px; }
  .scan-right { flex-wrap: wrap; gap: 6px; }
  .scan-body { overflow-x: auto; }
  .scan-body table { min-width: 500px; }
  th, td { padding: 10px 12px; font-size: 0.78rem; }
  .context-cell { max-width: 150px; }
  .modal { padding: 24px; }
}

/* ── Small phone ── */
@media (max-width: 480px) {
  .page { padding: 12px; }
  .metrics { grid-template-columns: 1fr; }
  .metric-card { flex-direction: row; align-items: center; gap: 14px; }
  .metric-icon { width: 36px; height: 36px; font-size: 1rem; }
  .metric-value { font-size: 1.3rem; }
}
</style>
