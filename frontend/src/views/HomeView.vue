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
      <input v-model="target" placeholder="Digite um IP ou domínio (ex: 127.0.0.1)" @keyup.enter="runScan" />
      <button @click="runScan" :disabled="loading">{{ loading ? 'Escaneando...' : 'Escanear' }}</button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result-box">
      <h2>Resultado — {{ result.target }}</h2>
      <p>Portas abertas: <strong>{{ result.total_open_ports }}</strong> | Total de findings: <strong>{{ result.total_findings }}</strong></p>
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
          <tr v-for="port in result.results" :key="port.port + port.service" :class="port.risk.toLowerCase()">
            <td>{{ port.port }}</td>
            <td>{{ port.service }}</td>
            <td>{{ port.risk }}</td>
            <td class="context">{{ port.context || '—' }}</td>
            <td class="banner">{{ port.banner || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
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
</script>

<style scoped>
.container { max-width: 800px; margin: 60px auto; padding: 0 20px; }
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
h2 { margin-bottom: 16px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 16px; text-align: left; border-bottom: 1px solid #21262d; }
th { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; }
tr.critical td { color: #f85149; }
tr.attention td { color: #e3b341; }
tr.common td { color: #3fb950; }
.context { font-size: 0.85rem; color: #8b949e; max-width: 300px; }
.banner { font-size: 0.8rem; color: #8b949e; font-family: monospace; }
</style>
