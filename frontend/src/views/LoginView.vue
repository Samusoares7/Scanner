<template>
  <div class="login-page">
    <!-- Ambient background -->
    <div class="ambient-grid" aria-hidden="true"></div>
    <div class="glow glow-primary" aria-hidden="true"></div>
    <div class="glow glow-accent" aria-hidden="true"></div>

    <div class="login-container">
      <!-- COLUNA ESQUERDA -->
      <div class="login-left">
        <!-- Brand -->
        <div class="brand">
          <div class="brand-icon-wrap">
            <div class="brand-icon-glow"></div>
            <div class="brand-icon">🛡️</div>
          </div>
          <div class="brand-text">
            <div class="brand-name">Scanner-Pro</div>
            <div class="brand-sub">painel de segurança ofensiva</div>
          </div>
        </div>

        <!-- Headline -->
        <div class="left-content">
          <div class="system-badge">
            <span class="badge-dot"></span>
            sistema online
          </div>

          <h1 class="headline">
            Entre no <span class="gradient-text">centro de operações</span> de segurança.
          </h1>

          <p class="headline-sub">
            Autenticação criptografada ponta-a-ponta. Acesso restrito a operadores
            autorizados — toda sessão é registrada e monitorada em tempo real.
          </p>

          <!-- Terminal -->
          <div class="terminal-card">
            <div class="terminal-topbar">
              <div class="terminal-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
              </div>
              <div class="terminal-title">⬛ AUTH-STREAM</div>
              <div class="terminal-tty">tty/0</div>
            </div>
            <div class="terminal-body">
              <div
                v-for="(line, i) in logs"
                :key="i"
                class="terminal-line"
                :class="{ 'line-active': i === logs.length - 1 }"
              >
                <span class="prompt">$</span>
                {{ line }}
                <span v-if="i === logs.length - 1" class="cursor"></span>
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">Uptime</div>
              <div class="stat-value">99.98%</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Sessões</div>
              <div class="stat-value">1.2k</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Bloqueios</div>
              <div class="stat-value critical">342</div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="left-footer">
          🔒 Conexão segura · TLS 1.3 · AES-256
        </div>
      </div>

      <!-- COLUNA DIREITA -->
      <div class="login-right">
        <div class="form-card">
          <!-- Glow interno do card -->
          <div class="card-glow" aria-hidden="true"></div>

          <div class="form-inner">
            <!-- Eyebrow -->
            <div class="form-eyebrow">
              🔏 ACESSO SEGURO
            </div>
            <h2 class="form-title">Autentique-se</h2>
            <p class="form-sub">Insira suas credenciais para entrar no painel.</p>

            <!-- Form -->
            <form @submit.prevent="doLogin" class="form">
              <!-- Usuário -->
              <div class="field">
                <label class="field-label">USUÁRIO DO OPERADOR</label>
                <div class="field-input" :class="{ focused: focusedField === 'username' }">
                  <span class="field-icon">👤</span>
                  <input
                    v-model="username"
                    type="text"
                    placeholder="admin"
                    autocomplete="username"
                    @focus="focusedField = 'username'"
                    @blur="focusedField = ''"
                  />
                </div>
              </div>

              <!-- Senha -->
              <div class="field">
                <label class="field-label">SENHA MESTRE</label>
                <div class="field-input" :class="{ focused: focusedField === 'password' }">
                  <span class="field-icon">🔒</span>
                  <input
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="••••••••••••"
                    autocomplete="current-password"
                    @focus="focusedField = 'password'"
                    @blur="focusedField = ''"
                  />
                  <button
                    type="button"
                    class="toggle-pwd"
                    @click="showPassword = !showPassword"
                    :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'"
                  >
                    {{ showPassword ? '🙈' : '👁️' }}
                  </button>
                </div>
              </div>

              <!-- Erro -->
              <div v-if="error" class="form-error">
                ⚠️ {{ error }}
              </div>

              <!-- Submit -->
              <button
                type="submit"
                class="btn-submit"
                :disabled="loading"
              >
                <span class="btn-shimmer"></span>
                <span v-if="loading" class="spinner"></span>
                {{ loading ? 'Autenticando...' : 'Entrar no painel →' }}
              </button>
            </form>

            <p class="form-footer">
              Acesso restrito. Toda tentativa de login é registrada e monitorada.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const focusedField = ref('')

const initialLogs = [
  '[boot] inicializando módulo de autenticação...',
  '[net]  handshake TLS 1.3 estabelecido',
  '[auth] aguardando credenciais do operador',
]

const rotatingLogs = [
  '[scan] varredura passiva ativa · 0 ameaças',
  '[vault] cofre de credenciais descriptografado',
  '[net]  latência do gateway: 12ms',
  '[auth] aguardando credenciais do operador',
  '[scan] 0 intrusões detectadas',
  '[sys]  todos os módulos operacionais',
]

const logs = ref([...initialLogs])
let logIndex = 0
let logInterval = null

onMounted(() => {
  logInterval = setInterval(() => {
    logs.value = [
      ...logs.value.slice(-6),
      rotatingLogs[logIndex % rotatingLogs.length]
    ]
    logIndex++
  }, 2200)
})

onUnmounted(() => {
  if (logInterval) clearInterval(logInterval)
})

const doLogin = async () => {
  if (!username.value || !password.value) return
  loading.value = true
  error.value = ''
  logs.value = [...logs.value.slice(-6), `[auth] autenticando ${username.value}...`]
  try {
    const response = await login(username.value, password.value)
    localStorage.setItem('token', response.data.access_token)
    logs.value = [...logs.value.slice(-6), '[auth] sessão criada · token jwt emitido']
    setTimeout(() => router.push('/dashboard'), 600)
  } catch (e) {
    error.value = 'Usuário ou senha incorretos'
    logs.value = [...logs.value.slice(-6), '[auth] ERRO: credenciais inválidas']
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Base ── */
.login-page {
  position: relative;
  min-height: 100vh;
  background: #060d1f;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Ambient ── */
.ambient-grid {
  pointer-events: none;
  position: absolute;
  inset: 0;
  opacity: 0.15;
  background-image:
    linear-gradient(rgba(255,255,255,0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.07) 1px, transparent 1px);
  background-size: 44px 44px;
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black 40%, transparent 100%);
  mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black 40%, transparent 100%);
}
.glow {
  pointer-events: none;
  position: absolute;
  border-radius: 50%;
  filter: blur(140px);
}
.glow-primary {
  width: 480px; height: 480px;
  top: -120px; left: 33%;
  background: #2563eb;
  opacity: 0.22;
}
.glow-accent {
  width: 420px; height: 420px;
  bottom: 0; right: 0;
  background: #06b6d4;
  opacity: 0.18;
}

/* ── Layout ── */
.login-container {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  max-width: 1100px;
  width: 100%;
  padding: 40px 32px;
  align-items: center;
}

/* ── Coluna esquerda ── */
.login-left {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}
.brand-icon-wrap {
  position: relative;
  width: 44px; height: 44px;
}
.brand-icon-glow {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: #2563eb;
  opacity: 0.5;
  filter: blur(8px);
}
.brand-icon {
  position: relative;
  width: 44px; height: 44px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  backdrop-filter: blur(12px);
}
.brand-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1;
}
.brand-sub {
  font-size: 0.7rem;
  color: #64748b;
  margin-top: 3px;
}

.left-content { display: flex; flex-direction: column; gap: 24px; }

.system-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #06b6d4;
  width: fit-content;
}
.badge-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.headline {
  font-size: 2.4rem;
  font-weight: 700;
  line-height: 1.2;
  color: #e2e8f0;
  letter-spacing: -0.02em;
}
.gradient-text {
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.headline-sub {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.7;
  max-width: 420px;
}

/* ── Terminal ── */
.terminal-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(12px);
}
.terminal-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.terminal-dots { display: flex; gap: 6px; }
.dot {
  width: 10px; height: 10px;
  border-radius: 50%;
}
.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }
.terminal-title {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: #64748b;
}
.terminal-tty {
  font-size: 0.65rem;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
}
.terminal-body {
  padding: 16px;
  height: 180px;
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.8;
}
.terminal-line { color: #64748b; }
.terminal-line.line-active { color: #e2e8f0; }
.prompt {
  color: #06b6d4;
  margin-right: 8px;
}
.cursor {
  display: inline-block;
  width: 6px; height: 14px;
  background: #2563eb;
  vertical-align: middle;
  margin-left: 4px;
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ── Stats ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.stat-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 14px 16px;
  backdrop-filter: blur(12px);
}
.stat-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #64748b;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: #e2e8f0;
}
.stat-value.critical { color: #ef4444; }

.left-footer {
  font-size: 0.72rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ── Coluna direita ── */
.login-right {
  display: flex;
  align-items: center;
  justify-content: center;
}
.form-card {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: rgba(12, 21, 40, 0.8);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 40px;
  backdrop-filter: blur(20px);
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,0.4);
}
.card-glow {
  pointer-events: none;
  position: absolute;
  top: -80px; right: -20px;
  width: 200px; height: 200px;
  border-radius: 50%;
  background: #2563eb;
  opacity: 0.2;
  filter: blur(60px);
}
.form-inner { position: relative; }

.form-eyebrow {
  font-size: 0.65rem;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.2em;
  color: #06b6d4;
  margin-bottom: 8px;
  text-transform: uppercase;
}
.form-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 6px;
}
.form-sub {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 28px;
}

.form { display: flex; flex-direction: column; gap: 18px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: #64748b;
  text-transform: uppercase;
}
.field-input {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.field-input.focused {
  border-color: #2563eb;
  background: rgba(255,255,255,0.06);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
}
.field-icon { font-size: 0.9rem; flex-shrink: 0; }
.field-input input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e2e8f0;
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
}
.field-input input::placeholder { color: #64748b; }
.toggle-pwd {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.toggle-pwd:hover { color: #e2e8f0; }

.form-error {
  font-size: 0.82rem;
  color: #ef4444;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.2);
  border-radius: 8px;
  padding: 10px 14px;
}

/* ── Submit button ── */
.btn-submit {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 10px 40px -10px rgba(37, 99, 235, 0.7);
  transition: opacity 0.2s, transform 0.1s;
  margin-top: 4px;
}
.btn-submit:hover { opacity: 0.92; }
.btn-submit:active { transform: scale(0.99); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

/* Shimmer effect */
.btn-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  transform: translateX(-100%);
  transition: transform 0.7s;
}
.btn-submit:hover .btn-shimmer { transform: translateX(100%); }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.5;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .login-container {
    grid-template-columns: 1fr;
    padding: 24px 16px;
  }
  .login-left { display: none; }
  .form-card { max-width: 100%; }
}
</style>
