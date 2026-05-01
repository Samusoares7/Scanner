<template>
  <div class="container">
    <div class="header">
      <div class="nav">
        <router-link to="/dashboard">Dashboard</router-link>
        <router-link to="/">Scanner</router-link>
      </div>
      <button class="logout" @click="logout">Sair</button>
    </div>

    <h1>🔍 Scanner</h1>
    <p class="subtitle">Varredura de portas TCP com classificação de risco</p>

    <div class="scan-box">
      <input
        v-model="target"
        placeholder="Digite um IP ou domínio"
        @keyup.enter="runScan"
      />
      <button @click="runScan" :disabled="loading">
        {{ loading ? 'Escaneando...' : 'Escanear' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result-box">
      <!-- Score de Segurança -->
      <div class="score-section">
        <div class="score-circle" :class="scoreClass">
          <span class="score-number">{{ score }}</span>
          <span class="score-label">/ 100</span>
        </div>
        <div class="score-info">
          <h2>Resultado — {{ result.target }}</h2>
          <p class="score-status" :class="scoreClass">{{ scoreLabel }}</p>
          <p class="score-summary">{{ summary }}</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="stats">
        <div class="stat">
          <span class="stat-value">{{ result.total_open_ports }}</span>
          <span class="stat-label">Portas Abertas</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ result.total_findings }}</span>
          <span class="stat-label">Total Findings</span>
        </div>
        <div class="stat critical">
          <span class="stat-value">{{ countRisk('CRITICAL') }}</span>
          <span class="stat-label">Críticos</span>
        </div>
        <div class="stat attention">
          <span class="stat-value">{{ countRisk('ATTENTION') }}</span>
          <span class="stat-label">Atenção</span>
        </div>
        <div class="stat common">
          <span class="stat-value">{{ countRisk('COMMON') }}</span>
          <span class="stat-label">Comuns</span>
        </div>
      </div>

      <!-- Tabela de findings -->
      <table>
        <thead>
          <tr>
            <th>Porta</th>
            <th>Serviço</th>
            <th>Risco</th>
            <th>Contexto</th>
            <th>Banner</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="port in result.results"
            :key="port.port + port.service"
            :class="port.risk.toLowerCase()"
          >
            <td>{{ port.port }}</td>
            <td>{{ port.service }}</td>
            <td>{{ port.risk }}</td>
            <td class="context">{{ port.context || '—' }}</td>
            <td class="banner">{{ port.banner || '' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { startScan } from '../services/api'

const target = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref('')
const router = useRouter()

const runScan = async () => {
  if (!target.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const response = await startScan(target.value)
    result.value = response.data
  } catch (e) {
    error.value = 'Erro ao escanear. Verifique o alvo e tente novamente.'
  } finally {
    loading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const countRisk = (risk) => {
  if (!result.value) return 0
  return result.value.results.filter(r => r.risk === risk).length
}

const score = computed(() => {
  if (!result.value) return 100
  let s = 100
  result.value.results.forEach(r => {
    if (r.risk === 'CRITICAL') s -= 20
    else if (r.risk === 'ATTENTION') s -= 8
    else if (r.risk === 'COMMON') s -= 2
  })
  return Math.max(0, s)
})

const scoreClass = computed(() => {
  if (score.value >= 80) return 'safe'
  if (score.value >= 50) return 'moderate'
  if (score.value >= 20) return 'high'
  return 'critical'
})

const scoreLabel = computed(() => {
  if (score.value >= 80) return '🟢 Baixo Risco'
  if (score.value >= 50) return '🟡 Risco Moderado'
  if (score.value >= 20) return '🔴 Alto Risco'
  return '🔴 Nível Crítico'
})

const summary = computed(() => {
  if (!result.value) return ''
  const findings = result.value.results
  const critical = findings.filter(r => r.risk === 'CRITICAL')
  const attention = findings.filter(r => r.risk === 'ATTENTION')
  const total = findings.length
  const targetValue = target.value.trim()

  // Detecta se foi digitado sem protocolo
  const hasNoProtocol = !targetValue.startsWith('http://') && !targetValue.startsWith('https://')
  const hasHttpFindings = findings.some(r => r.port === 80)
  const hasHttpsFindings = findings.some(r => r.port === 443)
  const mixedProtocol = hasNoProtocol && hasHttpFindings && hasHttpsFindings

  if (total === 0) {
    return 'Nenhum problema encontrado. Seu ambiente parece bem configurado para os itens verificados.'
  }

  if (critical.length === 0 && attention.length === 0) {
    return `Foram encontrados ${total} itens de baixo risco. Nenhum problema crítico detectado — seu ambiente está razoavelmente seguro.`
  }

  let text = ''

  // Mensagem contextual HTTP vs HTTPS
  if (mixedProtocol && score.value < 80) {
    text += `⚠️ Este site apresenta configuração de segurança diferente entre HTTP e HTTPS. Headers de segurança podem estar ausentes na camada HTTP, expondo usuários que acessam antes do redirecionamento. Tente escanear com "https://" para comparar. `
  }

  if (critical.length > 0) {
    const services = [...new Set(critical.map(r => r.service))].slice(0, 2).join(' e ')
    text += `Foram encontrados ${critical.length} problema${critical.length > 1 ? 's' : ''} crítico${critical.length > 1 ? 's' : ''} que precisam de atenção imediata — incluindo ${services}. `
  }

  if (attention.length > 0) {
    const hasHeaders = attention.some(r => r.service.includes('Header'))
    if (hasHeaders) {
      text += `Além disso, headers de segurança HTTP importantes não estão configurados, o que facilita ataques de clickjacking e injeção de conteúdo. `
    } else {
      text += `Também foram identificados ${attention.length} item${attention.length > 1 ? 'ns' : ''} que merecem atenção. `
    }
  }

  text += `Corrija os itens críticos antes de expor este ambiente publicamente.`

  return text
})
</script>

<style scoped>
.container { max-width: 860px; margin: 60px auto; padding: 0 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.nav { display: flex; gap: 16px; }
.nav a { color: #8b949e; text-decoration: none; }
.nav a:hover { color: #e6edf3; }
h1 { font-size: 2rem; margin-bottom: 8px; }
.subtitle { color: #8b949e; margin-bottom: 32px; }
.scan-box { display: flex; gap: 12px; margin-bottom: 24px; }
input { flex: 1; padding: 12px 16px; background: #161b22; border: 1px solid #30363d; border-radius: 8px; color: #e6edf3; font-size: 1rem; }
button { padding: 12px 24px; background: #238636; border: none; border-radius: 8px; color: white; font-size: 1rem; cursor: pointer; }
button:disabled { background: #1a4428; cursor: not-allowed; }
.logout { padding: 6px 16px; background: transparent; border: 1px solid #30363d; border-radius: 6px; color: #8b949e; cursor: pointer; }
.logout:hover { border-color: #f85149; color: #f85149; }
.error { color: #f85149; margin-bottom: 16px; }
.result-box { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }

/* Score */
.score-section { display: flex; gap: 24px; align-items: center; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #21262d; }
.score-circle { width: 100px; height: 100px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 4px solid; flex-shrink: 0; }
.score-circle.safe { border-color: #3fb950; color: #3fb950; }
.score-circle.moderate { border-color: #e3b341; color: #e3b341; }
.score-circle.high { border-color: #f85149; color: #f85149; }
.score-circle.critical { border-color: #f85149; color: #f85149; background: #f8514915; }
.score-number { font-size: 2rem; font-weight: bold; line-height: 1; }
.score-label { font-size: 0.75rem; color: #8b949e; }
.score-info { flex: 1; }
.score-info h2 { margin-bottom: 4px; }
.score-status { font-size: 0.9rem; margin-bottom: 8px; }
.score-status.safe { color: #3fb950; }
.score-status.moderate { color: #e3b341; }
.score-status.high { color: #f85149; }
.score-status.critical { color: #f85149; }
.score-summary { color: #8b949e; font-size: 0.9rem; line-height: 1.6; }

/* Stats */
.stats { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.stat { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px 20px; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-value { font-size: 1.5rem; font-weight: bold; }
.stat-label { font-size: 0.75rem; color: #8b949e; }
.stat.critical .stat-value { color: #f85149; }
.stat.attention .stat-value { color: #e3b341; }
.stat.common .stat-value { color: #3fb950; }

/* Tabela */
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 16px; text-align: left; border-bottom: 1px solid #21262d; }
th { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; }
tr.critical td { color: #f85149; }
tr.attention td { color: #e3b341; }
tr.common td { color: #3fb950; }
.context { font-size: 0.85rem; color: #8b949e !important; max-width: 300px; }
.banner { font-size: 0.8rem; color: #8b949e !important; font-family: monospace; }
</style>
