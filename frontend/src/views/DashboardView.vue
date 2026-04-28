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
      <div class="cards">
        <div class="card">
          <span class="card-label">Total de Scans</span>
          <span class="card-value">{{ stats.totalScans }}</span>
        </div>
        <div class="card">
          <span class="card-label">Portas Abertas</span>
          <span class="card-value">{{ stats.totalPorts }}</span>
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

      <div class="risk-bars">
        <h2>Distribuição de Risco</h2>
        <div class="bar-item">
          <span class="bar-label">CRITICAL</span>
          <div class="bar-track"><div class="bar-fill critical" :style="{ width: pct(stats.critical) }"></div></div>
          <span class="bar-pct">{{ pct(stats.critical) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">ATTENTION</span>
          <div class="bar-track"><div class="bar-fill attention" :style="{ width: pct(stats.attention) }"></div></div>
          <span class="bar-pct">{{ pct(stats.attention) }}</span>
        </div>
        <div class="bar-item">
          <span class="bar-label">COMMON</span>
          <div class="bar-track"><div class="bar-fill common" :style="{ width: pct(stats.common) }"></div></div>
          <span class="bar-pct">{{ pct(stats.common) }}</span>
        </div>
      </div>

      <div class="history">
        <h2>Histórico de Scans</h2>
        <table>
          <thead>
            <tr><th>#</th><th>Alvo</th><th>Portas</th><th>Criticidade</th><th>Data</th></tr>
          </thead>
          <tbody>
            <tr v-for="scan in scans" :key="scan.id">
              <td>{{ scan.id }}</td>
              <td>{{ scan.target }}</td>
              <td>{{ scan.total_open_ports }}</td>
              <td :class="topRisk(scan.results).toLowerCase()">{{ topRisk(scan.results) }}</td>
              <td>{{ formatDate(scan.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getScans, downloadReport } from '../services/api'

const exporting = ref(false)

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

const router = useRouter()
const scans = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await getScans()
    scans.value = response.data
  } catch (e) {
    router.push('/login')
  } finally {
    loading.value = false
  }
})

const stats = computed(() => {
  let totalPorts = 0, critical = 0, attention = 0, common = 0
  scans.value.forEach(scan => {
    scan.results.forEach(r => {
      totalPorts++
      if (r.risk === 'CRITICAL') critical++
      else if (r.risk === 'ATTENTION') attention++
      else common++
    })
  })
  return { totalScans: scans.value.length, totalPorts, critical, attention, common }
})

const pct = (val) => {
  if (stats.value.totalPorts === 0) return '0%'
  return Math.round((val / stats.value.totalPorts) * 100) + '%'
}

const topRisk = (results) => {
  if (results.some(r => r.risk === 'CRITICAL')) return 'CRITICAL'
  if (results.some(r => r.risk === 'ATTENTION')) return 'ATTENTION'
  return 'COMMON'
}

const formatDate = (dt) => new Date(dt).toLocaleDateString('pt-BR')

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
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
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 16px; text-align: left; border-bottom: 1px solid #21262d; }
th { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; }
.critical { color: #f85149; }
.attention { color: #e3b341; }
.common { color: #3fb950; }

.btn-report { padding: 10px 20px; background: #1f6feb; border: none; border-radius: 8px; color: white; font-size: 0.9rem; cursor: pointer; }
.btn-report:hover { background: #388bfd; }
.btn-report:disabled { background: #1c3a5e; cursor: not-allowed; }
</style>
