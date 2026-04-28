<template>
  <div class="login-container">
    <div class="login-box">
      <h1>🔐 Scanner-Pro</h1>
      <p class="subtitle">Acesso restrito</p>
      <div class="form">
        <input v-model="username" type="text" placeholder="Usuário" @keyup.enter="doLogin" />
        <input v-model="password" type="password" placeholder="Senha" @keyup.enter="doLogin" />
        <button @click="doLogin" :disabled="loading">{{ loading ? 'Entrando...' : 'Entrar' }}</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
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
.login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; }
.login-box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 40px; width: 100%; max-width: 400px; }
h1 { font-size: 1.8rem; margin-bottom: 8px; text-align: center; }
.subtitle { color: #8b949e; text-align: center; margin-bottom: 32px; }
.form { display: flex; flex-direction: column; gap: 12px; }
input { padding: 12px 16px; background: #0d1117; border: 1px solid #30363d; border-radius: 8px; color: #e6edf3; font-size: 1rem; }
button { padding: 12px; background: #238636; border: none; border-radius: 8px; color: white; font-size: 1rem; cursor: pointer; margin-top: 8px; }
button:disabled { background: #1a4428; cursor: not-allowed; }
.error { color: #f85149; text-align: center; margin-top: 16px; }
</style>
