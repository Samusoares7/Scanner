<template>
  <div class="container">
    <div class="header">
      <h1>🔐 Scanner-Pro</h1>
      <button class="btn-report" @click="exportPDF" :disabled="exporting">
        {{ exporting ? 'Gerando...' : '📄 Exportar Relatório PDF' }}
      </button>
      <div class="nav">
        <router-link to="/dashboard">Dashboard</router-link>
        <router-link to="/">Scanner</router-link>
        <button class="logout" @click="logout">Sair</button>
      </div>
    </div>

    <div v-if="loading" class="loading">Carregando dados...</div>

    <div v-else>
      <!-- Cards Gerais -->
      <div class="cards">
        <div class="card">
          <span class="card-label">Total de Scans</span>
          <span class="card-value">{{ stats.totalScans }}</span>
        </div>
        <div class="card">
          <span class="card-label">Alvos Únicos</span>
          <span class="card-value">{{ stats.uniqueTargets }}</span>
        </div>
        <div class="card critical">
          <span class="card-label">🔴 Críticas</span>
          <span class="card-value">{{ stats.critical }}</span>
        </div>
        <div class="card attention">
          <span class="card-label">🟡 Atenção</span>
          <span class="card-value">{{ stats.attention }}</span>
        </div>
        <div class="card common">
          <span class="card-label">🟢 Comuns</span>
          <span class="card-value">{{ stats.common }}</span>
        </div>
      </div>

      <!-- Distribuição de Risco -->
      <div class="risk-bars">
        <h2>Distribuição de Risco</h2>
        <div class="bar-item">
          <span class="bar-label">CRITICAL</span>
          <div class="bar-track">
            <div class="bar-fill critical" :style="{ width: pct(stats.critical) }"></div>
          </div>
          <span class="bar-pct">{{ pct(stats.critical) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">ATTENTION</span>
          <div class="bar-track">
            <div class="bar-fill attention" :style="{ width: pct(stats.attention) }"></div>
          </div>
          <span class="bar-pct">{{ pct(stats.attention) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">COMMON</span>
          <div class="bar-track">
            <div class="bar-fill common" :style="{ width: pct(stats.common) }"></div>
          </div>
          <span class="bar-pct">{{ pct(stats.common) }}</span>
        </div>
      </div>

      <!-- Histórico por Alvo -->
      <div class="history">
        <div class="history-header">
          <h2>Histórico de Scans por Alvo</h2>
          <button class="btn-clear" @click="confirmClear" :disabled="scans.length === 0">
            🗑 Limpar Histórico
          </button>
        </div>

        <div v-if="scans.length === 0" class="empty">
          Nenhum scan realizado ainda.
        </div>

        <div v-else>
          <div v-for="scan in scans" :key="scan.id" class="scan-card">
            <div class="scan-card-header">
              <div class="scan-target">
                <span class="target-ip">{{ scan.target }}</span>
                <span class="scan-date">{{ formatDate(scan.created_at) }}</span>
              </div>
              <div class="scan-summary">
                <span class="badge">{{ scan.total_open_ports }} portas abertas</span>
                <span class="badge">{{ scan.results.length }} findings</span>
                <span class="badge" :class="topRisk(scan.results).toLowerCase()">
                  {{ topRisk(scan.results) }}
                </span>
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Porta</th>
                  <th>Serviço</th>
                  <th>Risco</th>
                  <th>Contexto</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="port in scan.results" :key="port.port + port.service" :class="port.risk.toLowerCase()">
                  <td>{{ port.port }}</td>
                  <td>{{ port.service }}</td>
                  <td>{{ port.risk }}</td>
                  <td class="context">{{ port.context || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmação -->
    <div v-if="showConfirm" class="modal-overlay">
      <div class="modal">
        <h3>Limpar Histórico</h3>
        <p>Tem certeza? Todos os scans serão apagados permanentemente.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm = false">Cancelar</button>
          <button class="btn-confirm" @click="clearHistory">Confirmar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getScans, clearScans, downloadReport } from '../services/api'

const router = useRouter()
const scans = ref([])
const loading = ref(true)
const showConfirm = ref(false)
const exporting = ref(false)

onMounted(async () => {
  await loadScans()
})

const loadScans = async () => {
  loading.value = true
  try {
    const response = await getScans()
    scans.value = response.data
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
  return {
    totalScans: scans.value.length,
    uniqueTargets: targets.size,
    critical,
    attention,
    common
  }
})

const pct = (val) => {
  const total = stats.value.critical + stats.value.attention + stats.value.common
  if (total === 0) return '0%'
  return Math.round((val / total) * 100) + '%'
}

const topRisk = (results) => {
  if (!results || results.length === 0) return 'COMMON'
  if (results.some(r => r.risk === 'CRITICAL')) return 'CRITICAL'
  if (results.some(r => r.risk === 'ATTENTION')) return 'ATTENTION'
  return 'COMMON'
}

const formatDate = (dt) => {
  return new Date(dt).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const confirmClear = () => { showConfirm.value = true }

const clearHistory = async () => {
  try {
    await clearScans()
    scans.value = []
    showConfirm.value = false
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
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('Erro ao gerar relatório')
  } finally {
    exporting.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
h1 { font-size: 1.8rem; }
.nav { display: flex; gap: 16px; align-items: center; }
.nav a { color: #8b949e; text-decoration: none; }
.nav a:hover { color: #e6edf3; }
.logout { padding: 6px 16px; background: transparent; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; cursor: pointer; }
.logout:hover { border-color: #f85149; color: #f85149; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-bottom: 32px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 8px; }
.card-label { color: #8b949e; font-size: 0.85rem; }
.card-value { font-size: 2rem; font-weight: bold; }
.card.critical { border-color: #f85149; }
.card.attention { border-color: #e3b341; }
.card.common { border-color: #3fb950; }
.risk-bars { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; margin-bottom: 32px; }
h2 { margin-bottom: 20px; font-size: 1rem; color: #8b949e; text-transform: uppercase; }
.bar-item { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.bar-label { width: 80px; font-size: 0.85rem; color: #8b949e; }
.bar-track { flex: 1; background: #21262d; border-radius: 4px; height: 8px; }
.bar-fill { height: 8px; border-radius: 4px; transition: width 0.5s; }
.bar-fill.critical { background: #f85149; }
.bar-fill.attention { background: #e3b341; }
.bar-fill.common { background: #3fb950; }
.bar-pct { width: 40px; font-size: 0.85rem; color: #8b949e; }
.history { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }
.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-clear { padding: 8px 16px; background: transparent; border: 1px solid #f85149; border-radius: 6px; color: #f85149; cursor: pointer; font-size: 0.85rem; }
.btn-clear:hover { background: #f8514920; }
.btn-clear:disabled { opacity: 0.4; cursor: not-allowed; }
.empty { color: #8b949e; text-align: center; padding: 32px; }
.scan-card { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
.scan-card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid #21262d; }
.scan-target { display: flex; flex-direction: column; gap: 4px; }
.target-ip { font-size: 1.1rem; font-weight: bold; color: #e6edf3; }
.scan-date { font-size: 0.8rem; color: #8b949e; }
.scan-summary { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { padding: 4px 10px; background: #161b22; border: 1px solid #30363d; border-radius: 20px; font-size: 0.8rem; color: #8b949e; }
.badge.critical { border-color: #f85149; color: #f85149; }
.badge.attention { border-color: #e3b341; color: #e3b341; }
.badge.common { border-color: #3fb950; color: #3fb950; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 16px; text-align: left; border-bottom: 1px solid #21262d; }
th { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; }
.critical td { color: #f85149; }
.attention td { color: #e3b341; }
.common td { color: #3fb950; }
.context { font-size: 0.85rem; color: #8b949e !important; max-width: 300px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 32px; max-width: 400px; width: 90%; }
.modal h3 { margin-bottom: 12px; }
.modal p { color: #8b949e; margin-bottom: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.btn-cancel { padding: 8px 20px; background: transparent; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; cursor: pointer; }
.btn-confirm { padding: 8px 20px; background: #f85149; border: none; border-radius: 6px; color: white; cursor: pointer; }

.btn-report { padding: 10px 20px; background: #1f6feb; border: none; border-radius: 8px; color: white; font-size: 0.9rem; cursor: pointer; }
.btn-report:hover { background: #388bfd; }
.btn-report:disabled { background: #1c3a5e; cursor: not-allowed; }
</style>
