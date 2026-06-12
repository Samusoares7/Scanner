<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-brand">
        <span class="brand-icon">🛡️</span>
        <div>
          <div class="brand-name">Scanner-Pro</div>
          <div class="brand-sub">Security Operations Center</div>
        </div>
      </div>
      <div class="login-headline">
        Audite sua infraestrutura antes que outros o façam.
      </div>
      <div class="login-features">
        <div class="feature-item">
          <span class="feature-icon">🔍</span>
          <span>Varredura de portas TCP com contexto de risco</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🛡️</span>
          <span>Análise de headers de segurança HTTP</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📊</span>
          <span>Dashboard com score de segurança</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📄</span>
          <span>Relatórios PDF profissionais</span>
        </div>
      </div>
    </div>
    <div class="login-right">
      <div class="login-box">
        <h2>Acesso ao Sistema</h2>
        <p class="login-desc">Entre com suas credenciais para continuar</p>
        <div class="form">
          <div class="field">
            <label>Usuário</label>
            <input v-model="username" type="text" placeholder="admin" @keyup.enter="doLogin" />
          </div>
          <div class="field">
            <label>Senha</label>
            <input v-model="password" type="password" placeholder="••••••••" @keyup.enter="doLogin" />
          </div>
          <button @click="doLogin" :disabled="loading" class="btn-login">
            {{ loading ? 'Autenticando...' : 'Entrar' }}
          </button>
        </div>
        <div v-if="error" class="login-error">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/api'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()

const doLogin = async () => {
  if (!username.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    const response = await login(username.value, password.value)
    localStorage.setItem('token', response.data.access_token)
    router.push('/dashboard')
  } catch (e) {
    error.value = 'Usuário ou senha incorretos'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { display: flex; min-height: 100vh; }
.login-left {
  flex: 1;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  padding: 60px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.login-brand { display: flex; align-items: center; gap: 16px; }
.brand-icon { font-size: 2.5rem; }
.brand-name { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); }
.brand-sub { font-size: 0.75rem; color: var(--text-secondary); letter-spacing: 0.05em; }
.login-headline { font-size: 2rem; font-weight: 700; color: var(--text-primary); line-height: 1.3; max-width: 400px; }
.login-features { display: flex; flex-direction: column; gap: 16px; }
.feature-item { display: flex; align-items: center; gap: 12px; color: var(--text-secondary); font-size: 0.9rem; }
.feature-icon { font-size: 1.2rem; }
.login-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
}
.login-box { width: 100%; }
.login-box h2 { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px; }
.login-desc { color: var(--text-secondary); margin-bottom: 32px; font-size: 0.9rem; }
.form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 0.8rem; color: var(--text-secondary); font-weight: 500; }
.field input {
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s;
}
.field input:focus { outline: none; border-color: var(--accent-blue); }
.btn-login {
  padding: 12px;
  background: var(--accent-blue);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  transition: opacity 0.2s;
}
.btn-login:hover { opacity: 0.9; }
.btn-login:disabled { opacity: 0.5; cursor: not-allowed; }
.login-error { color: var(--critical); font-size: 0.85rem; margin-top: 16px; text-align: center; }
</style>
