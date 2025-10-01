import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import NProgress from 'nprogress'

// 创建axios实例
const service = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    NProgress.start()
    
    // 每次请求都重新读取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      console.log('[Request] Token已添加到请求头')
    } else {
      console.warn('[Request] 未找到Token')
    }
    
    console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`)
    
    return config
  },
  (error) => {
    NProgress.done()
    console.error('[Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    NProgress.done()
    return response.data
  },
  (error) => {
    NProgress.done()
    
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // 避免重复提示和跳转
          const currentPath = router.currentRoute.value.path
          if (currentPath !== '/login') {
            ElMessage.error('未授权，请先登录')
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_info')
            
            // 延迟跳转，避免与路由守卫冲突
            setTimeout(() => {
              router.push('/login')
            }, 100)
          }
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(response.data?.error || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default service

