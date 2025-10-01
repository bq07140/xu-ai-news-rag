# 项目结构说明

## 📁 完整目录结构

```
backend/
│
├── app.py                      # 应用主入口，Flask应用工厂
├── config.py                   # 配置文件（开发/生产/测试环境）
├── models.py                   # 数据库模型定义
├── vector_store.py             # FAISS向量存储管理
├── requirements.txt            # Python依赖包列表
├── .gitignore                  # Git忽略文件配置
├── env.example                 # 环境变量示例文件
│
├── README.md                   # 完整项目文档
├── QUICKSTART.md              # 快速开始指南
├── API_EXAMPLES.md            # API使用示例集合
├── PROJECT_STRUCTURE.md       # 本文件
│
├── run.sh                      # Linux/Mac启动脚本
├── test_api.py                 # API测试脚本
│
├── routes/                     # API路由模块
│   ├── __init__.py
│   ├── auth.py                # 认证相关接口
│   ├── documents.py           # 文档管理接口
│   ├── search.py              # 搜索功能接口
│   └── analysis.py            # 数据分析接口
│
├── services/                   # 业务逻辑服务层
│   ├── __init__.py
│   ├── document_parser.py     # 文档解析服务
│   ├── search_service.py      # 搜索服务（网络搜索、LLM）
│   └── analysis_service.py    # 数据分析服务
│
├── tests/                      # 测试用例
│   ├── __init__.py
│   ├── conftest.py            # pytest配置和fixtures
│   ├── test_auth.py           # 认证功能测试
│   ├── test_documents.py      # 文档管理测试
│   ├── test_search.py         # 搜索功能测试
│   └── test_analysis.py       # 数据分析测试
│
├── uploads/                    # 上传文件临时存储（运行时生成）
├── faiss_index/               # FAISS向量索引存储（运行时生成）
│   ├── faiss.index            # 向量索引文件
│   └── doc_mapping.pkl        # 文档ID映射文件
│
├── logs/                      # 日志文件（可选）
└── xu_news_rag.db             # SQLite数据库文件（运行时生成）
```

## 📄 核心文件说明

### 🔧 配置与入口

#### `app.py`
应用主入口文件，包含：
- Flask应用工厂函数
- 扩展初始化（数据库、JWT、CORS）
- 蓝图注册
- 错误处理器
- 健康检查端点

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    # 配置加载
    # 扩展初始化
    # 路由注册
    return app
```

#### `config.py`
配置类定义，支持多环境：
- `DevelopmentConfig`: 开发环境
- `ProductionConfig`: 生产环境
- `TestingConfig`: 测试环境

关键配置项：
- 数据库URI
- JWT密钥和过期时间
- FAISS索引路径
- 文件上传限制
- 嵌入模型名称

#### `models.py`
数据库模型定义：
- `User`: 用户模型（认证）
- `Document`: 文档模型（知识库）
- `SearchHistory`: 搜索历史模型

关系：
- User → Document (一对多)
- User → SearchHistory (一对多)

#### `vector_store.py`
FAISS向量存储管理类：
- 嵌入模型加载
- 向量索引管理（增删查）
- 语义相似度检索
- 索引持久化

## 🛣️ 路由模块 (routes/)

### `auth.py` - 认证接口
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/refresh` | POST | 刷新Token |
| `/api/auth/me` | GET | 获取当前用户 |
| `/api/auth/logout` | POST | 用户登出 |

### `documents.py` - 文档管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/documents/` | GET | 获取文档列表 |
| `/api/documents/<id>` | GET | 获取文档详情 |
| `/api/documents/<id>` | PUT | 更新文档 |
| `/api/documents/<id>` | DELETE | 删除文档 |
| `/api/documents/batch-delete` | POST | 批量删除 |
| `/api/documents/upload` | POST | 上传文档 |
| `/api/documents/categories` | GET | 获取分类 |
| `/api/documents/sources` | GET | 获取来源 |

### `search.py` - 搜索功能
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/search/semantic` | POST | 语义检索 |
| `/api/search/web` | POST | 联网搜索 |
| `/api/search/combined` | POST | 组合搜索 |
| `/api/search/history` | GET | 搜索历史 |
| `/api/search/history/<id>` | DELETE | 删除历史 |

### `analysis.py` - 数据分析
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/analysis/report` | GET | 分析报告 |
| `/api/analysis/keywords` | POST | 关键词提取 |
| `/api/analysis/category-distribution` | GET | 分类分布 |
| `/api/analysis/source-distribution` | GET | 来源分布 |
| `/api/analysis/time-trend` | GET | 时间趋势 |
| `/api/analysis/stats` | GET | 统计信息 |

## 🔨 服务层 (services/)

### `document_parser.py`
文档解析服务，支持格式：
- PDF (PyPDF2)
- DOCX (python-docx)
- TXT (纯文本)
- Excel (openpyxl)
- Markdown

主要方法：
```python
DocumentParser.parse_file(file_path, filename) -> Dict
```

### `search_service.py`
搜索服务：

**WebSearchService**:
- 网络搜索API集成
- 模拟搜索（开发模式）

**LLMService**:
- Ollama集成
- 搜索结果摘要生成
- 降级处理

### `analysis_service.py`
数据分析服务：
- 关键词提取（jieba + TF-IDF）
- 分类/来源分布统计
- 时间趋势分析
- 综合报告生成

主要方法：
```python
AnalysisService.extract_keywords(texts, topK)
AnalysisService.generate_summary_report(documents, time_range)
```

## 🧪 测试模块 (tests/)

### 测试覆盖范围

| 模块 | 测试文件 | 覆盖功能 |
|------|----------|----------|
| 认证 | `test_auth.py` | 注册、登录、Token |
| 文档 | `test_documents.py` | CRUD、上传、筛选 |
| 搜索 | `test_search.py` | 语义检索、联网搜索 |
| 分析 | `test_analysis.py` | 统计、关键词、报告 |

### 运行测试
```bash
# 所有测试
pytest

# 单个模块
pytest tests/test_auth.py

# 带覆盖率
pytest --cov=. --cov-report=html
```

## 💾 数据存储

### SQLite数据库 (`xu_news_rag.db`)
表结构：
- `users`: 用户信息
- `documents`: 文档数据
- `search_history`: 搜索历史

### FAISS向量索引 (`faiss_index/`)
- `faiss.index`: FAISS索引文件
- `doc_mapping.pkl`: 文档ID映射（Python pickle）

索引维护：
- 自动保存（每次修改后）
- 支持增量更新
- 删除需要重建索引

## 📦 依赖包说明

### 核心依赖
- **Flask**: Web框架
- **Flask-SQLAlchemy**: ORM
- **Flask-JWT-Extended**: JWT认证
- **sentence-transformers**: 嵌入模型
- **faiss-cpu**: 向量检索
- **jieba**: 中文分词

### 文档处理
- **PyPDF2**: PDF解析
- **python-docx**: DOCX解析
- **openpyxl**: Excel解析
- **markdown**: Markdown解析

### 数据分析
- **scikit-learn**: TF-IDF
- **numpy**: 数值计算
- **pandas**: 数据处理

### 测试
- **pytest**: 测试框架
- **pytest-flask**: Flask测试支持

## 🔄 数据流

### 1. 文档上传流程
```
用户上传 → 文件保存 → 文档解析 → 
数据库存储 → 向量编码 → FAISS索引 → 
返回结果
```

### 2. 语义检索流程
```
用户查询 → 查询向量化 → FAISS检索 → 
相似度排序 → 数据库查询 → 结果返回
```

### 3. 智能搜索流程
```
用户查询 → 知识库检索 → 
结果充足? → 是: 返回结果
          → 否: 联网搜索 → LLM摘要 → 
          返回组合结果
```

## 🚀 扩展点

### 添加新的API端点
1. 在 `routes/` 下创建或修改蓝图
2. 定义路由和处理函数
3. 在 `app.py` 中注册蓝图

### 添加新的文档格式支持
1. 在 `services/document_parser.py` 中添加解析方法
2. 更新 `ALLOWED_EXTENSIONS` 配置

### 切换数据库
1. 修改 `config.py` 中的 `DATABASE_URI`
2. 安装对应的数据库驱动（如 `psycopg2`）
3. 运行迁移（如果使用 Flask-Migrate）

### 集成新的搜索引擎
1. 在 `services/search_service.py` 中实现新的搜索类
2. 配置API密钥和URL
3. 更新 `routes/search.py` 调用新服务

## 📊 性能考虑

### 瓶颈点
1. **向量检索**: 数据量大时考虑使用IVF索引
2. **LLM推理**: 响应较慢，考虑异步处理
3. **文件上传**: 大文件解析耗时，使用后台任务

### 优化建议
1. 使用Redis缓存热点数据
2. 数据库查询添加适当索引
3. 使用Gunicorn多进程部署
4. 考虑分离向量检索服务

## 🔐 安全考虑

### 已实现
- ✅ 密码bcrypt加密
- ✅ JWT Token认证
- ✅ 文件类型白名单
- ✅ SQL注入防护（ORM）

### 待加强
- 文件内容安全扫描
- API速率限制
- HTTPS强制
- CSRF保护（前后端分离时）

## 📝 开发规范

### 代码风格
- 遵循PEP 8
- 使用类型提示
- 添加文档字符串

### 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
test: 添加测试
refactor: 代码重构
```

---

**维护者**: XU AI Team  
**最后更新**: 2025-10-01  
**版本**: v1.0.0


