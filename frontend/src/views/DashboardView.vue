<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <span>Welcome, {{ username }}</span>
        <button @click="handleLogout">Logout</button>
      </div>
    </header>

    <main class="dashboard-content">
      <div v-if="loading" class="loading">Loading statistics...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <template v-else>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_items.toLocaleString() }}</div>
            <div class="stat-label">Items</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_properties.toLocaleString() }}</div>
            <div class="stat-label">Properties</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_lexemes.toLocaleString() }}</div>
            <div class="stat-label">Lexemes</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_statements.toLocaleString() }}</div>
            <div class="stat-label">Statements</div>
          </div>
          <div class="stat-card highlight">
            <div class="stat-value">{{ stats.total_edits.toLocaleString() }}</div>
            <div class="stat-label">Total Edits</div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { statsService, authService, type GeneralStats } from '@/services/api'

const router = useRouter()

const username = ref(localStorage.getItem('username') || 'User')
const stats = ref<GeneralStats>({
  total_items: 0,
  total_properties: 0,
  total_lexemes: 0,
  total_statements: 0,
  total_edits: 0
})
const loading = ref(true)
const error = ref('')

const loadStats = async () => {
  loading.value = true
  error.value = ''

  try {
    stats.value = await statsService.getGeneralStats()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load statistics'
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  authService.logout()
  router.push('/login')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard-header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  color: #667eea;
  font-size: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info span {
  color: #555;
}

.user-info button {
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.user-info button:hover {
  opacity: 0.9;
}

.dashboard-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading,
.error-message {
  text-align: center;
  padding: 2rem;
}

.error-message {
  color: #dc3545;
  background: #ffe6e6;
  border-radius: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.highlight .stat-label {
  color: rgba(255, 255, 255, 0.8);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 0.5rem;
}

.stat-card.highlight .stat-value {
  color: white;
}

.stat-label {
  color: #666;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
