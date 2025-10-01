# XU-News-AI-RAG 前端系统

个性化新闻智能知识库系统 - Vue 3 前端应用

## 📋 项目简介

这是 XU-News-AI-RAG 系统的前端部分，基于 Vue 3 + Element Plus 构建，提供用户友好的界面来管理新闻知识库、执行智能检索和查看数据分析。

## ✨ 功能特性

### 1. 用户认证 ✅
- 用户注册（用户名、邮箱、密码）
- 用户登录（JWT Token认证）
- 会话保持
- 安全退出

### 2. 知识库管理 ✅
- **文档列表展示**
  - 分页显示（默认每页20条）
  - 多维度筛选（分类、时间范围）
  - 实时刷新
  
- **文档操作**
  - 单条删除（二次确认）
  - 批量删除
  - 元数据编辑（标题、分类、标签、备注）
  - 文档详情查看
  
- **文件上传**
  - 支持格式：PDF、DOCX、TXT、Excel、Markdown
  - 拖拽上传
  - 上传进度显示
  - 分类管理

### 3. 智能检索 ✅
- **多种检索模式**
  - 语义检索（基于向量相似度）
  - 联网搜索（实时网络查询）
  - 智能组合（知识库+网络）
  
- **搜索配置**
  - 相似度阈值调整
  - 搜索历史记录
  - 结果高亮显示
  
- **结果展示**
  - 相似度评分
  - 分类标签
  - 时间排序

### 4. 数据分析 ✅
- **实时统计**
  - 文档总数
  - 近7天新增
  - 向量索引大小
  - 分类数量
  
- **可视化图表**
  - 分类分布饼图
  - 来源分布饼图
  - Top10关键词柱状图
  - 时间趋势折线图
  
- **综合报告**
  - 关键词提取分析
  - 多维度数据统计
  - 时间范围筛选

## 🛠 技术栈

- **核心框架**: Vue 3 (Composition API)
- **构建工具**: Vite 4
- **UI组件库**: Element Plus 2.3
- **状态管理**: Pinia 2
- **路由管理**: Vue Router 4
- **HTTP客户端**: Axios
- **图表库**: ECharts 5 + Vue-ECharts
- **日期处理**: Day.js
- **加载进度**: NProgress

## 📦 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口
│   │   └── index.js      # API封装
│   ├── assets/           # 资源文件
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # 状态管理
│   │   └── user.js
│   ├── utils/            # 工具函数
│   │   └── request.js    # Axios封装
│   ├── views/            # 页面组件
│   │   ├── Login.vue     # 登录/注册
│   │   ├── Documents.vue # 知识库管理
│   │   ├── Search.vue    # 智能检索
│   │   └── Analysis.vue  # 数据分析
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html
├── vite.config.js        # Vite配置
├── package.json
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将运行在 `http://localhost:3000`

### 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

## ⚙️ 配置说明

### API代理配置

在 `vite.config.js` 中配置后端API代理：

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // 后端地址
        changeOrigin: true
      }
    }
  }
})
```

### 环境变量

创建 `.env` 文件：

```bash
# 应用标题
VITE_APP_TITLE=XU-News-AI-RAG

# API基础URL（可选，默认使用代理）
VITE_API_BASE_URL=http://localhost:5000/api
```

## 📱 页面路由

| 路径 | 页面 | 说明 | 认证 |
|------|------|------|------|
| `/login` | 登录/注册 | 用户认证页面 | ❌ |
| `/documents` | 知识库管理 | 文档CRUD操作 | ✅ |
| `/search` | 智能检索 | 语义检索和联网搜索 | ✅ |
| `/analysis` | 数据分析 | 统计图表和报告 | ✅ |

## 🔐 认证流程

### 登录

1. 用户输入用户名和密码
2. 调用 `/api/auth/login` 接口
3. 后端返回 JWT Token
4. Token 存储在 localStorage
5. 自动跳转到首页

### Token管理

```javascript
// 自动添加Token到请求头
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 401自动跳转登录
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

## 📡 API接口对接

### 接口基础URL

```
开发环境: http://localhost:5000/api (通过Vite代理)
生产环境: 根据部署配置
```

### 主要接口

#### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取用户信息
- `POST /auth/logout` - 用户登出

#### 文档管理
- `GET /documents/` - 获取文档列表
- `GET /documents/:id` - 获取文档详情
- `PUT /documents/:id` - 更新文档
- `DELETE /documents/:id` - 删除文档
- `POST /documents/batch-delete` - 批量删除
- `POST /documents/upload` - 上传文档
- `GET /documents/categories` - 获取分类列表

#### 搜索功能
- `POST /search/semantic` - 语义检索
- `POST /search/web` - 联网搜索
- `POST /search/combined` - 组合搜索
- `GET /search/history` - 搜索历史

#### 数据分析
- `GET /analysis/stats` - 统计信息
- `POST /analysis/keywords` - 关键词提取
- `GET /analysis/category-distribution` - 分类分布
- `GET /analysis/source-distribution` - 来源分布
- `GET /analysis/time-trend` - 时间趋势
- `GET /analysis/report` - 综合报告

## 🎨 UI组件

### Element Plus

本项目使用 Element Plus 作为UI组件库，主要组件包括：

- **布局**: Container, Header, Aside, Main
- **表单**: Form, Input, Select, Upload, DatePicker
- **数据展示**: Table, Pagination, Tag, Card, Descriptions
- **反馈**: Message, MessageBox, Loading, Progress
- **导航**: Menu, Breadcrumb, Dropdown
- **图表**: 集成 ECharts

### 图表配置

使用 Vue-ECharts 封装 ECharts：

```vue
<template>
  <v-chart :option="chartOption" style="height: 400px" />
</template>

<script setup>
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'

use([PieChart, TooltipComponent])

const chartOption = ref({
  // ECharts配置
})
</script>
```

## 🔍 功能使用指南

### 1. 文档上传

1. 点击"上传文档"按钮
2. 选择分类（可新建）
3. 选择文件（支持PDF、Word等）
4. 点击上传
5. 等待解析完成

### 2. 智能检索

1. 输入搜索关键词
2. 选择检索模式：
   - 语义检索：仅搜索知识库
   - 智能组合：优先知识库，不足时联网
   - 联网搜索：直接网络搜索
3. 调整相似度阈值（可选）
4. 查看结果

### 3. 数据分析

- **统计卡片**：显示实时统计数据
- **分类/来源分布**：饼图展示数据分布
- **关键词分析**：柱状图显示热门词汇
- **时间趋势**：折线图展示数据增长
- **综合报告**：详细的分析报告

## 🐛 故障排查

### 无法连接后端

1. 确认后端服务已启动
2. 检查代理配置（vite.config.js）
3. 查看浏览器控制台错误

### Token过期

- 自动跳转到登录页面
- 重新登录即可

### 文件上传失败

1. 检查文件大小（<50MB）
2. 确认文件格式支持
3. 查看后端日志

### 图表不显示

1. 检查数据是否加载成功
2. 确认 ECharts 组件已正确导入
3. 查看浏览器控制台错误

## 📈 性能优化

### 已实现

- ✅ 路由懒加载
- ✅ 组件按需导入
- ✅ API请求拦截和缓存
- ✅ 图片懒加载
- ✅ 长列表虚拟滚动（可选）

### 建议优化

- 使用虚拟滚动优化大列表
- 启用 PWA 支持
- 实现数据缓存策略
- 添加骨架屏加载

## 🔒 安全特性

- ✅ JWT Token认证
- ✅ 路由权限守卫
- ✅ XSS防护（Vue自动转义）
- ✅ HTTPS部署（生产环境）
- ✅ Token自动刷新机制

## 🌐 浏览器兼容

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 📝 开发规范

### 代码风格

```bash
# ESLint检查
npm run lint
```

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 🚢 部署指南

### 使用Nginx

1. 构建项目：
```bash
npm run build
```

2. Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📄 许可证

MIT License

## 👥 开发团队

XU AI Team

## 📞 联系方式

- 技术支持：查看 [后端README](../backend/README.md)
- 问题反馈：提交 Issue

---

**版本**: v1.0.0  
**更新日期**: 2025-10-01  
**文档状态**: ✅ 完整


