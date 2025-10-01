# XU-News-AI-RAG 后端系统

个性化新闻智能知识库系统的后端API服务

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [API文档](#api文档)
- [测试](#测试)
- [部署](#部署)
- [常见问题](#常见问题)

## 📖 项目简介

XU-News-AI-RAG 后端系统是一个基于 Flask 的 RESTful API 服务，提供智能新闻知识库管理、语义检索、联网查询和数据分析等功能。系统采用 FAISS 向量数据库进行高效的语义检索，支持多种文档格式上传和解析。

## 🛠 技术栈

- **Web框架**: Flask 3.0
- **数据库**: SQLite (可扩展至 PostgreSQL)
- **向量数据库**: FAISS
- **嵌入模型**: all-MiniLM-L6-v2 (Sentence Transformers)
- **认证**: JWT (Flask-JWT-Extended)
- **文档解析**: PyPDF2, python-docx, openpyxl
- **中文处理**: jieba (分词、关键词提取)
- **测试**: pytest

## ✨ 功能特性

### 1. 用户认证系统 (F-AUTH-001)
- ✅ 用户注册 (用户名、邮箱、密码)
- ✅ 用户登录 (JWT Token)
- ✅ 密码加密存储 (bcrypt)
- ✅ Token刷新
- ✅ 登录状态验证
- ✅ 用户信息获取

### 2. 知识库内容管理 (F-KB-001)
- ✅ 文档列表展示 (分页、排序)
- ✅ 多维度筛选 (分类、来源、时间范围)
- ✅ 文档详情查看
- ✅ 元数据编辑 (标签、分类、备注)
- ✅ 单条/批量删除
- ✅ 文件上传 (PDF, DOCX, TXT, Excel, Markdown)
- ✅ 自动文档解析和入库

### 3. 智能语义检索 (F-SEARCH-001)
- ✅ 基于FAISS的向量检索
- ✅ 相似度评分
- ✅ 结果排序和过滤
- ✅ 搜索历史记录
- ✅ 自动触发联网查询

### 4. 智能联网查询 (F-WEB-001)
- ✅ 网络搜索API集成
- ✅ LLM摘要生成 (支持Ollama)
- ✅ 组合搜索 (知识库+网络)
- ✅ 降级处理机制

### 5. 数据聚类分析 (F-ANALYSIS-001)
- ✅ 关键词提取 (TF-IDF)
- ✅ Top10关键词统计
- ✅ 分类/来源分布分析
- ✅ 时间趋势分析
- ✅ 综合分析报告

## 🏗 系统架构

```
backend/
├── app.py                  # 应用入口
├── config.py              # 配置文件
├── models.py              # 数据库模型
├── vector_store.py        # FAISS向量存储
├── requirements.txt       # 依赖包
├── .gitignore            # Git忽略文件
│
├── routes/               # API路由
│   ├── auth.py          # 认证接口
│   ├── documents.py     # 文档管理接口
│   ├── search.py        # 搜索接口
│   └── analysis.py      # 分析接口
│
├── services/            # 业务服务
│   ├── document_parser.py    # 文档解析
│   ├── search_service.py     # 搜索服务
│   └── analysis_service.py   # 分析服务
│
└── tests/               # 测试用例
    ├── conftest.py
    ├── test_auth.py
    ├── test_documents.py
    ├── test_search.py
    └── test_analysis.py
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip 20+
- (可选) Ollama (用于LLM功能)

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

**注意**: 首次安装会自动下载嵌入模型 `all-MiniLM-L6-v2` (约90MB)，请确保网络连接正常。

### 3. 配置环境变量

创建 `.env` 文件 (参考 `.env.example`):

```bash
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
DATABASE_URI=sqlite:///xu_news_rag.db
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.6
MAX_SEARCH_RESULTS=10
UPLOAD_FOLDER=uploads
```

### 4. 初始化数据库

```bash
python app.py
```

首次运行会自动创建数据库和表结构。

### 5. 启动服务

```bash
# 开发模式
export FLASK_ENV=development
python app.py

# 生产模式
export FLASK_ENV=production
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 6. 验证安装

访问健康检查端点：

```bash
curl http://localhost:5000/health
```

返回：
```json
{
  "status": "healthy",
  "message": "XU-News-AI-RAG API is running"
}
```

## 📚 API文档

### 基础URL

```
http://localhost:5000/api
```

### 认证方式

除了注册和登录接口，所有API都需要在请求头中携带JWT Token：

```
Authorization: Bearer <access_token>
```

### API端点概览

#### 🔐 认证接口 (`/api/auth`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | ❌ |
| POST | `/auth/login` | 用户登录 | ❌ |
| POST | `/auth/refresh` | 刷新Token | ✅ |
| GET | `/auth/me` | 获取当前用户信息 | ✅ |
| POST | `/auth/logout` | 用户登出 | ✅ |

#### 📄 文档管理 (`/api/documents`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/documents/` | 获取文档列表 | ✅ |
| GET | `/documents/<id>` | 获取文档详情 | ✅ |
| PUT | `/documents/<id>` | 更新文档元数据 | ✅ |
| DELETE | `/documents/<id>` | 删除文档 | ✅ |
| POST | `/documents/batch-delete` | 批量删除文档 | ✅ |
| POST | `/documents/upload` | 上传文档 | ✅ |
| GET | `/documents/categories` | 获取分类列表 | ✅ |
| GET | `/documents/sources` | 获取来源列表 | ✅ |

#### 🔍 搜索接口 (`/api/search`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/search/semantic` | 语义检索 | ✅ |
| POST | `/search/web` | 联网搜索 | ✅ |
| POST | `/search/combined` | 组合搜索 | ✅ |
| GET | `/search/history` | 获取搜索历史 | ✅ |
| DELETE | `/search/history/<id>` | 删除搜索历史 | ✅ |

#### 📊 数据分析 (`/api/analysis`)

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/analysis/report` | 获取分析报告 | ✅ |
| POST | `/analysis/keywords` | 提取关键词 | ✅ |
| GET | `/analysis/category-distribution` | 分类分布 | ✅ |
| GET | `/analysis/source-distribution` | 来源分布 | ✅ |
| GET | `/analysis/time-trend` | 时间趋势 | ✅ |
| GET | `/analysis/stats` | 统计信息 | ✅ |

### 详细API示例

#### 1. 用户注册

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

响应：
```json
{
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2025-10-01T10:00:00"
  }
}
```

#### 2. 用户登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

响应：
```json
{
  "message": "登录成功",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

#### 3. 上传文档

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@document.pdf" \
  -F "category=科技"
```

#### 4. 语义检索

```bash
curl -X POST http://localhost:5000/api/search/semantic \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能最新进展",
    "k": 10,
    "threshold": 0.6
  }'
```

响应：
```json
{
  "query": "人工智能最新进展",
  "results": [
    {
      "id": 1,
      "title": "AI技术突破",
      "summary": "...",
      "similarity": 0.85,
      "created_at": "2025-10-01T10:00:00"
    }
  ],
  "count": 1,
  "trigger_web_search": false
}
```

#### 5. 获取分析报告

```bash
curl -X GET "http://localhost:5000/api/analysis/report?time_range=7days" \
  -H "Authorization: Bearer <access_token>"
```

## 🧪 测试

### 运行所有测试

```bash
cd backend
pytest
```

### 运行特定测试模块

```bash
# 测试认证功能
pytest tests/test_auth.py

# 测试文档管理
pytest tests/test_documents.py

# 测试搜索功能
pytest tests/test_search.py

# 测试分析功能
pytest tests/test_analysis.py
```

### 查看测试覆盖率

```bash
pytest --cov=. --cov-report=html
```

### 测试报告

测试覆盖以下场景：
- ✅ 用户注册/登录/认证
- ✅ 文档CRUD操作
- ✅ 文件上传和解析
- ✅ 语义检索和联网搜索
- ✅ 数据分析和统计
- ✅ 错误处理和边界情况

## 🚢 部署

### 使用 Gunicorn (生产环境)

1. 安装 Gunicorn:
```bash
pip install gunicorn
```

2. 启动服务:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

参数说明：
- `-w 4`: 4个工作进程
- `-b 0.0.0.0:5000`: 绑定地址和端口
- `app:app`: 模块名:应用名

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：

```bash
docker build -t xu-news-rag-backend .
docker run -p 5000:5000 -v $(pwd)/data:/app/data xu-news-rag-backend
```

### 环境变量配置

生产环境建议配置：

```bash
export FLASK_ENV=production
export SECRET_KEY=<strong-secret-key>
export JWT_SECRET_KEY=<strong-jwt-key>
export DATABASE_URI=postgresql://user:pass@host:5432/dbname
```

## ❓ 常见问题

### 1. 嵌入模型下载失败

**问题**: 首次启动时模型下载超时或失败。

**解决方案**:
- 检查网络连接，确保能访问 Hugging Face
- 手动下载模型到 `~/.cache/torch/sentence_transformers/`
- 使用镜像源: `export HF_ENDPOINT=https://hf-mirror.com`

### 2. FAISS索引损坏

**问题**: 向量检索报错或返回异常结果。

**解决方案**:
```bash
# 删除索引文件并重建
rm -rf faiss_index/
# 重启应用会自动创建新索引
python app.py
```

### 3. 数据库迁移

**问题**: 更新模型后需要迁移数据库。

**解决方案**:
```bash
# 使用Flask-Migrate
pip install Flask-Migrate
flask db init
flask db migrate -m "描述"
flask db upgrade
```

### 4. JWT Token过期

**问题**: Token过期后无法访问API。

**解决方案**:
- 使用刷新Token端点获取新的访问Token
- 调整Token过期时间 (config.py 中的 `JWT_ACCESS_TOKEN_EXPIRES`)

### 5. 文件上传大小限制

**问题**: 上传大文件失败。

**解决方案**:
```python
# 在 config.py 中调整
MAX_UPLOAD_SIZE = 104857600  # 100MB
```

### 6. Ollama连接失败

**问题**: LLM摘要功能不可用。

**解决方案**:
- 确保Ollama服务已启动: `ollama serve`
- 检查模型是否已下载: `ollama pull qwen2.5:3b`
- 验证连接: `curl http://localhost:11434/api/tags`

### 7. 中文分词效果差

**问题**: jieba分词或关键词提取效果不理想。

**解决方案**:
```python
# 添加自定义词典
import jieba
jieba.load_userdict('custom_dict.txt')
```

## 📈 性能优化建议

1. **数据库优化**
   - 为常用查询字段添加索引
   - 使用PostgreSQL替代SQLite
   - 启用数据库连接池

2. **向量检索优化**
   - 使用FAISS的IVF索引 (数据量>10万时)
   - 批量添加文档而非单条添加
   - 定期优化索引

3. **缓存策略**
   - 使用Redis缓存热点数据
   - 缓存搜索结果和分析报告
   - 实现查询去重

4. **异步处理**
   - 使用Celery处理文件上传
   - 异步更新向量索引
   - 后台生成分析报告

## 📝 开发计划

- [ ] 支持多语言 (English, 日本語)
- [ ] 实现文档版本控制
- [ ] 添加权限管理系统
- [ ] 集成更多搜索引擎
- [ ] 支持实时推送通知
- [ ] 添加API限流功能
- [ ] 实现分布式部署

## 📄 许可证

MIT License

## 👥 贡献者

- XU AI Team

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- Email: support@xu-news-rag.com
- Issue: 提交GitHub Issue

---

**版本**: v1.0.0  
**更新日期**: 2025-10-01  
**文档状态**: ✅ 完整


