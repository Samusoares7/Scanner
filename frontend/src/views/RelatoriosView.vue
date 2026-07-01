<template>
  <div class="page">
    <div class="topbar">
      <div>
        <h1 class="page-title">Relatórios</h1>
        <span class="page-sub">Exporte e gerencie relatórios de segurança</span>
      </div>
    </div>

    <div class="reports-layout">
      <div class="report-card">
        <div class="report-icon">📄</div>
        <div class="report-info">
          <div class="report-title">Relatório Completo PDF</div>
          <div class="report-desc">Exporta todos os scans com sumário executivo e detalhamento por alvo, classificação de risco e contexto.</div>
        </div>
        <button class="btn-export" @click="exportPDF" :disabled="exporting">
          {{ exporting ? 'Gerando...' : '⬇ Exportar PDF' }}
        </button>
      </div>

      <div class="stats-summary" v-if="summary">
        <h2>Resumo dos Dados</h2>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-val">{{ summary.totalScans }}</span>
            <span class="summary-lbl">Total de Scans</span>
          </div>
          <div class="summary-item">
            <span class="summary-val">{{ summary.uniqueTargets }}</span>
            <span class="summary-lbl">Alvos Únicos</span>
          </div>
          <div class="summary-item critical">
            <span class="summary-val">{{ summary.critical }}</span>
            <span class="summary-lbl">Findings Críticos</span>
          </div>
          <div class="summary-item attention">
            <span class="summary-val">{{ summary.attention }}</span>
            <span class="summary-lbl">Findings Atenção</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getScans, downloadReport } from '../services/api'

const exporting = ref(false)
const summary = ref(null)

onMounted(async () => {
  try {
    const response = await getScans()
    const scans = response.data
    let critical = 0, attention = 0
    const targets = new Set()
    scans.forEach(scan => {
      targets.add(scan.target)
      scan.results.forEach(r => {
        if (r.risk === 'CRITICAL') critical++
        else if (r.risk === 'ATTENTION') attention++
      })
    })
    summary.value = { totalScans: scans.length, uniqueTargets: targets.size, critical, attention }
  } catch (e) {}
})

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
.page { padding: 32px; max-width: 800px; }
.topbar { margin-bottom: 32px; }
.page-title { font-size: 1.6rem; font-weight: 700; }
.page-sub { font-size: 0.85rem; color: var(--text-secondary); }
.reports-layout { display: flex; flex-direction: column; gap: 24px; }
.report-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  display: flex; align-items: center; gap: 20px;
}
.report-icon { font-size: 2.5rem; }
.report-info { flex: 1; }
.report-title { font-size: 1rem; font-weight: 600; margin-bottom: 4px; }
.report-desc { font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; }
.btn-export {
  padding: 10px 20px;
  background: var(--accent-blue);
  border: none; border-radius: 8px;
  color: white; font-size: 0.85rem;
  cursor: pointer; font-weight: 500;
  transition: opacity 0.2s;
}
.btn-export:hover { opacity: 0.9; }
.btn-export:disabled { opacity: 0.5; cursor: not-allowed; }

.stats-summary {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  display: flex; flex-direction: column; gap: 16px;
}
.stats-summary h2 { font-size: 1rem; font-weight: 600; }
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.summary-item { display: flex; flex-direction: column; gap: 4px; }
.summary-val { font-size: 1.5rem; font-weight: 700; }
.summary-lbl { font-size: 0.72rem; color: var(--text-secondary); }
.summary-item.critical .summary-val { color: var(--critical); }
.summary-item.attention .summary-val { color: var(--attention); }

/* ── Mobile ── */
@media (max-width: 768px) {
  .page { padding: 16px; }
  .page-title { font-size: 1.3rem; }
  .report-card { flex-direction: column; align-items: flex-start; gap: 16px; padding: 20px; }
  .report-icon { font-size: 2rem; }
  .btn-export { width: 100%; text-align: center; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .summary-val { font-size: 1.2rem; }
  .stats-summary { padding: 20px; }
}

/* ── Small phone ── */
@media (max-width: 480px) {
  .page { padding: 12px; }
  .summary-grid { grid-template-columns: 1fr; }
}
</style>
