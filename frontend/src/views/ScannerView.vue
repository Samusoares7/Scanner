<template>
  <div class="page">
    <div class="topbar">
      <div>
        <h1 class="page-title">Scanner</h1>
        <span class="page-sub">Inicie uma nova varredura de segurança</span>
      </div>
    </div>

    <div class="scanner-layout">
      <!-- Painel de configuração -->
      <div class="config-panel">
        <div class="panel-section">
          <label class="panel-label">Alvo</label>
          <input
            v-model="target"
            class="target-input"
            placeholder="Digite o IP "
            @keyup.enter="runScan"
          />
        </div>
        <button class="btn-scan" @click="runScan" :disabled="loading">
          <span v-if="loading" class="scanning-dot"></span>
          {{ loading ? 'Escaneando...' : '🔍 Iniciar Scan' }}
        </button>
        <div v-if="error" class="scan-error">{{ error }}</div>
      </div>

      <!-- Resultado -->
      <div class="result-panel" v-if="result">
        <!-- Score -->
        <div class="score-card">
          <div class="score-circle" :class="scoreClass">
            <span class="score-num">{{ score }}</span>
            <span class="score-sub">/ 100</span>
          </div>
          <div class="score-details">
            <div class="score-target">{{ result.target }}</div>
            <div class="score-status" :class="scoreClass">{{ scoreLabel }}</div>
            <div class="score-summary">{{ summary }}</div>
          </div>
        </div>

        <!-- Stats -->
        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-val">{{ result.total_open_ports }}</span>
            <span class="stat-lbl">Portas Abertas</span>
          </div>
          <div class="stat-item">
            <span class="stat-val">{{ result.total_findings }}</span>
            <span class="stat-lbl">Total Findings</span>
          </div>
          <div class="stat-item critical">
            <span class="stat-val">{{ countRisk('CRITICAL') }}</span>
            <span class="stat-lbl">Críticos</span>
          </div>
          <div class="stat-item attention">
            <span class="stat-val">{{ countRisk('ATTENTION') }}</span>
            <span class="stat-lbl">Atenção</span>
          </div>
          <div class="stat-item common">
            <span class="stat-val">{{ countRisk('COMMON') }}</span>
            <span class="stat-lbl">Comuns</span>
          </div>
        </div>

        <!-- Tabela -->
        <div class="result-table">
          <table>
            <thead>
              <tr>
                <th>PORTA</th>
                <th>SERVIÇO</th>
                <th>RISCO</th>
                <th>CONTEXTO</th>
                <th>BANNER</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in result.results" :key="r.port + r.service">
                <td class="mono">{{ r.port }}</td>
                <td>{{ r.service }}</td>
                <td><span class="risk-badge" :class="r.risk.toLowerCase()">{{ r.risk }}</span></td>
                <td class="context-cell">{{ r.context || '—' }}</td>
                <td class="mono-sm">{{ r.banner || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty state -->
      <div class="empty-panel" v-else-if="!loading">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">Nenhum scan iniciado</div>
        <div class="empty-sub">Digite um IP ou domínio e clique em Iniciar Scan</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { startScan } from '../services/api'

const target = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref('')

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

const countRisk = (risk) => result.value?.results.filter(r => r.risk === risk).length || 0

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
  const hasNoProtocol = !targetValue.startsWith('http://') && !targetValue.startsWith('https://')
  const hasHttpFindings = findings.some(r => r.port === 80)
  const hasHttpsFindings = findings.some(r => r.port === 443)
  const mixedProtocol = hasNoProtocol && hasHttpFindings && hasHttpsFindings

  if (total === 0) return 'Nenhum problema encontrado. Seu ambiente parece bem configurado.'
  if (critical.length === 0 && attention.length === 0) return `Foram encontrados ${total} itens de baixo risco. Nenhum problema crítico detectado.`

  let text = ''
  if (mixedProtocol && score.value < 80) text += `⚠️ Configuração diferente entre HTTP e HTTPS detectada. Tente escanear com "https://" para comparar. `
  if (critical.length > 0) {
    const services = [...new Set(critical.map(r => r.service))].slice(0, 2).join(' e ')
    text += `${critical.length} problema${critical.length > 1 ? 's' : ''} crítico${critical.length > 1 ? 's' : ''} encontrado${critical.length > 1 ? 's' : ''} — incluindo ${services}. `
  }
  if (attention.length > 0) {
    const hasHeaders = attention.some(r => r.service.includes('Header'))
    if (hasHeaders) text += `Headers de segurança HTTP ausentes facilitam ataques de clickjacking e injeção de conteúdo. `
    else text += `${attention.length} item${attention.length > 1 ? 'ns' : ''} de atenção identificado${attention.length > 1 ? 's' : ''}. `
  }
  text += `Corrija os itens críticos antes de expor este ambiente publicamente.`
  return text
})
</script>

<style scoped>
.page { padding: 32px; }
.topbar { margin-bottom: 32px; }
.page-title { font-size: 1.6rem; font-weight: 700; }
.page-sub { font-size: 0.85rem; color: var(--text-secondary); }
.scanner-layout { display: flex; flex-direction: column; gap: 24px; max-width: 900px; }
.config-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel-label { font-size: 0.8rem; color: var(--text-secondary); font-weight: 500; margin-bottom: 6px; display: block; }
.target-input {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'JetBrains Mono', monospace;
  transition: border-color 0.2s;
}
.target-input:focus { outline: none; border-color: var(--accent-blue); }
.btn-scan {
  padding: 12px 24px;
  background: var(--accent-blue);
  border: none; border-radius: 8px;
  color: white; font-size: 0.95rem;
  font-weight: 600; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  align-self: flex-start;
  transition: opacity 0.2s;
}
.btn-scan:hover { opacity: 0.9; }
.btn-scan:disabled { opacity: 0.5; cursor: not-allowed; }
.scanning-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: white;
  animation: pulse 1s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.scan-error { color: var(--critical); font-size: 0.85rem; }

/* Score */
.score-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 24px;
  align-items: center;
}
.score-circle {
  width: 90px; height: 90px;
  border-radius: 50%;
  border: 3px solid;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  flex-shrink: 0;
}
.score-circle.safe { border-color: var(--common); color: var(--common); }
.score-circle.moderate { border-color: var(--attention); color: var(--attention); }
.score-circle.high { border-color: var(--critical); color: var(--critical); }
.score-circle.critical { border-color: var(--critical); color: var(--critical); background: #ef444410; }
.score-num { font-size: 1.8rem; font-weight: 700; line-height: 1; }
.score-sub { font-size: 0.7rem; color: var(--text-secondary); }
.score-details { flex: 1; }
.score-target { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); font-size: 0.95rem; margin-bottom: 4px; }
.score-status { font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; }
.score-status.safe { color: var(--common); }
.score-status.moderate { color: var(--attention); }
.score-status.high, .score-status.critical { color: var(--critical); }
.score-summary { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6; }

/* Stats */
.result-stats {
  display: flex; gap: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
.stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-val { font-size: 1.5rem; font-weight: 700; }
.stat-lbl { font-size: 0.72rem; color: var(--text-secondary); text-align: center; }
.stat-item.critical .stat-val { color: var(--critical); }
.stat-item.attention .stat-val { color: var(--attention); }
.stat-item.common .stat-val { color: var(--common); }

/* Tabela */
.result-table {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}
table { width: 100%; border-collapse: collapse; }
th { padding: 12px 16px; text-align: left; font-size: 0.7rem; color: var(--text-secondary); letter-spacing: 0.05em; border-bottom: 1px solid var(--border); background: var(--bg-tertiary); }
td { padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #1e2d4a20; }
.mono { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); }
.mono-sm { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--text-secondary); }
.risk-badge { padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
.risk-badge.critical { background: #ef444420; color: var(--critical); }
.risk-badge.attention { background: #f59e0b20; color: var(--attention); }
.risk-badge.common { background: #10b98120; color: var(--common); }
.context-cell { color: var(--text-secondary); font-size: 0.82rem; max-width: 280px; }

/* Empty */
.empty-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 60px;
  text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.empty-icon { font-size: 3rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; }
.empty-sub { color: var(--text-secondary); font-size: 0.85rem; }

/* ── Mobile ── */
@media (max-width: 768px) {
  .page { padding: 16px; }
  .page-title { font-size: 1.3rem; }
  .score-card { flex-direction: column; text-align: center; gap: 16px; padding: 20px; }
  .score-circle { align-self: center; }
  .result-stats { flex-wrap: wrap; gap: 8px; padding: 16px; }
  .stat-item { flex: 1 1 calc(50% - 8px); min-width: 0; }
  .result-table { overflow-x: auto; }
  .result-table table { min-width: 550px; }
  th, td { padding: 10px 12px; font-size: 0.78rem; }
  .context-cell { max-width: 150px; }
  .empty-panel { padding: 40px 20px; }
  .btn-scan { align-self: stretch; justify-content: center; }
}

/* ── Small phone ── */
@media (max-width: 480px) {
  .page { padding: 12px; }
  .stat-item { flex: 1 1 100%; }
  .score-num { font-size: 1.5rem; }
}
</style>
