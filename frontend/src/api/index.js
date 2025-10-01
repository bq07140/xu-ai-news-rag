import request from '@/utils/request'

// ========== 认证相关 API ==========
export const authAPI = {
  // 用户注册
  register(data) {
    return request({
      url: '/auth/register',
      method: 'post',
      data
    })
  },

  // 用户登录
  login(data) {
    return request({
      url: '/auth/login',
      method: 'post',
      data
    })
  },

  // 获取当前用户信息
  getUserInfo() {
    return request({
      url: '/auth/me',
      method: 'get'
    })
  },

  // 登出
  logout() {
    return request({
      url: '/auth/logout',
      method: 'post'
    })
  }
}

// ========== 文档管理 API ==========
export const documentAPI = {
  // 获取文档列表
  getDocuments(params) {
    return request({
      url: '/documents/',
      method: 'get',
      params
    })
  },

  // 获取文档详情
  getDocument(id) {
    return request({
      url: `/documents/${id}`,
      method: 'get'
    })
  },

  // 更新文档
  updateDocument(id, data) {
    return request({
      url: `/documents/${id}`,
      method: 'put',
      data
    })
  },

  // 删除文档
  deleteDocument(id) {
    return request({
      url: `/documents/${id}`,
      method: 'delete'
    })
  },

  // 批量删除文档
  batchDelete(ids) {
    return request({
      url: '/documents/batch-delete',
      method: 'post',
      data: { ids }
    })
  },

  // 上传文档
  uploadDocument(formData) {
    return request({
      url: '/documents/upload',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取分类列表
  getCategories() {
    return request({
      url: '/documents/categories',
      method: 'get'
    })
  },

  // 获取来源列表
  getSources() {
    return request({
      url: '/documents/sources',
      method: 'get'
    })
  }
}

// ========== 搜索相关 API ==========
export const searchAPI = {
  // 语义检索
  semanticSearch(data) {
    return request({
      url: '/search/semantic',
      method: 'post',
      data
    })
  },

  // 联网搜索
  webSearch(data) {
    return request({
      url: '/search/web',
      method: 'post',
      data
    })
  },

  // 组合搜索
  combinedSearch(data) {
    return request({
      url: '/search/combined',
      method: 'post',
      data
    })
  },

  // 获取搜索历史
  getSearchHistory(params) {
    return request({
      url: '/search/history',
      method: 'get',
      params
    })
  },

  // 删除搜索历史
  deleteHistory(id) {
    return request({
      url: `/search/history/${id}`,
      method: 'delete'
    })
  }
}

// ========== 数据分析 API ==========
export const analysisAPI = {
  // 获取分析报告
  getReport(params) {
    return request({
      url: '/analysis/report',
      method: 'get',
      params
    })
  },

  // 提取关键词
  extractKeywords(data) {
    return request({
      url: '/analysis/keywords',
      method: 'post',
      data
    })
  },

  // 获取分类分布
  getCategoryDistribution() {
    return request({
      url: '/analysis/category-distribution',
      method: 'get'
    })
  },

  // 获取来源分布
  getSourceDistribution() {
    return request({
      url: '/analysis/source-distribution',
      method: 'get'
    })
  },

  // 获取时间趋势
  getTimeTrend(params) {
    return request({
      url: '/analysis/time-trend',
      method: 'get',
      params
    })
  },

  // 获取统计信息
  getStatistics() {
    return request({
      url: '/analysis/stats',
      method: 'get'
    })
  }
}


