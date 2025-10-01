<template>
  <div class="search-page">
    <!-- Search Box -->
    <el-card class="search-card" shadow="never">
      <el-input
        v-model="query"
        placeholder="Enter your search query..."
        :prefix-icon="Search"
        size="large"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch">Search</el-button>
        </template>
      </el-input>

      <div class="search-options">
        <el-space>
          <span>Search Type:</span>
          <el-radio-group v-model="searchType" size="small">
            <el-radio-button value="semantic">Semantic Search</el-radio-button>
            <el-radio-button value="combined">Smart Combined</el-radio-button>
            <el-radio-button value="web">Web Search</el-radio-button>
          </el-radio-group>

          <el-divider direction="vertical" />

          <span>Similarity Threshold:</span>
          <el-slider
            v-model="threshold"
            :min="0.3"
            :max="1"
            :step="0.1"
            :show-tooltip="true"
            style="width: 120px"
          />
        </el-space>
      </div>
    </el-card>

    <!-- Search Results -->
    <el-card v-if="hasSearched" class="results-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>
            Search Results
            <el-tag v-if="!loading" type="info" size="small">
              {{ results.length }} items
            </el-tag>
          </span>
          <el-button text :icon="Delete" @click="clearResults">Clear</el-button>
        </div>
      </template>

      <el-skeleton v-if="loading" :rows="5" animated />

      <div v-else-if="results.length === 0" class="empty-state">
        <el-empty description="No results found" />
      </div>

      <div v-else class="results-list">
        <!-- Knowledge Base Results -->
        <div v-if="kbResults.length > 0" class="result-section">
          <h3 class="section-title">
            <el-icon><Document /></el-icon>
            Knowledge Base Results
          </h3>
          <el-timeline>
            <el-timeline-item
              v-for="item in kbResults"
              :key="item.id"
              :timestamp="formatDate(item.created_at)"
              placement="top"
            >
              <el-card shadow="hover">
                <div class="result-item">
                  <div class="result-header">
                    <h4 class="result-title">{{ item.title }}</h4>
                    <el-tag v-if="item.match_score !== undefined" type="success" size="small">
                      Match: {{ (item.match_score * 100).toFixed(0) }}%
                    </el-tag>
                    <el-tag v-if="item.matched_keywords && item.matched_keywords.length" type="warning" size="small">
                      {{ item.matched_keywords.join(', ') }}
                    </el-tag>
                  </div>

                  <div class="result-meta">
                    <el-tag size="small" type="info">{{ item.category }}</el-tag>
                    <span class="meta-item">Source: {{ item.source }}</span>
                  </div>

                  <div class="result-summary">{{ item.summary }}</div>

                  <div class="result-tags">
                    <el-tag
                      v-for="tag in item.tags"
                      :key="tag"
                      size="small"
                      effect="plain"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- Web Search Results -->
        <div v-if="webResults.length > 0" class="result-section">
          <h3 class="section-title">
            <el-icon><Link /></el-icon>
            Web Search Results
          </h3>

          <el-alert
            v-if="webSummary"
            :title="webSummary"
            type="info"
            :closable="false"
            style="margin-bottom: 16px"
          />

          <el-space direction="vertical" style="width: 100%">
            <el-card
              v-for="(item, index) in webResults"
              :key="index"
              shadow="hover"
            >
              <div class="web-result">
                <h4 class="result-title">{{ item.title }}</h4>
                <p class="result-snippet">{{ item.snippet }}</p>
                <a :href="item.url" target="_blank" class="result-link">
                  <el-icon><Link /></el-icon>
                  {{ item.url }}
                </a>
              </div>
            </el-card>
          </el-space>
        </div>
      </div>
    </el-card>

    <!-- Search History -->
    <el-card v-if="history.length > 0" class="history-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Search History</span>
          <el-button text :icon="Delete" @click="clearHistory">Clear</el-button>
        </div>
      </template>

      <el-space wrap>
        <el-tag
          v-for="item in history"
          :key="item.id"
          closable
          @click="query = item.query; handleSearch()"
          @close="deleteHistoryItem(item.id)"
          style="cursor: pointer"
        >
          {{ item.query }}
        </el-tag>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Document, Link, Delete } from '@element-plus/icons-vue'
import { searchAPI } from '@/api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const query = ref('')
const searchType = ref('combined')
const threshold = ref(0.6)
const loading = ref(false)
const hasSearched = ref(false)

const results = ref([])
const kbResults = ref([])
const webResults = ref([])
const webSummary = ref('')
const history = ref([])

// Format date
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// Execute search
const handleSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('Please enter search content')
    return
  }

  loading.value = true
  hasSearched.value = true
  results.value = []
  kbResults.value = []
  webResults.value = []
  webSummary.value = ''

  try {
    let res
    const searchData = {
      query: query.value,
      threshold: threshold.value
    }

    switch (searchType.value) {
      case 'semantic':
        res = await searchAPI.semanticSearch(searchData)
        kbResults.value = res.results
        break

      case 'combined':
        res = await searchAPI.combinedSearch(searchData)
        kbResults.value = res.knowledge_base_results
        if (res.web_search_triggered) {
          webResults.value = res.web_results
          webSummary.value = res.web_summary
        }
        break

      case 'web':
        res = await searchAPI.webSearch({
          query: query.value,
          num_results: 3
        })
        webResults.value = res.results
        webSummary.value = res.summary
        break
    }

    results.value = [...kbResults.value, ...webResults.value]
    fetchHistory()
  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    loading.value = false
  }
}

// Clear results
const clearResults = () => {
  results.value = []
  kbResults.value = []
  webResults.value = []
  webSummary.value = ''
  hasSearched.value = false
  query.value = ''
}

// Fetch search history
const fetchHistory = async () => {
  try {
    const res = await searchAPI.getSearchHistory({ limit: 10 })
    history.value = res.history
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

// Clear history
const clearHistory = () => {
  history.value = []
}

// Delete history item
const deleteHistoryItem = async (id) => {
  try {
    await searchAPI.deleteHistory(id)
    history.value = history.value.filter((item) => item.id !== id)
  } catch (error) {
    console.error('Failed to delete history:', error)
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.search-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  flex-shrink: 0;
}

.search-options {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.results-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-section {
  padding-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.result-title {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-summary {
  color: #606266;
  line-height: 1.6;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.web-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-snippet {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.result-link {
  color: #409eff;
  font-size: 13px;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-link:hover {
  text-decoration: underline;
}

.empty-state {
  padding: 60px 0;
}

.history-card {
  flex-shrink: 0;
}
</style>


