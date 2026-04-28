import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = (username, password) => {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)
  return api.post('/token', params)
}

export const startScan = (target) => api.post('/scan', { target })
export const getScans = () => api.get('/scans')
export const getScanById = (id) => api.get(`/scans/${id}`)
export const downloadReport = () =>
  api.get('/report/pdf', { responseType: 'blob' })
