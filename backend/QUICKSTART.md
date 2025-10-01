# 快速开始指南

## 🚀 5分钟快速部署

### 步骤 1: 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

**注意**: 首次安装会下载嵌入模型 (~90MB)，需要几分钟时间。

### 步骤 2: 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 步骤 3: 测试API

打开新终端，运行测试脚本：

```bash
python test_api.py
```

## 📝 基础使用流程

### 1. 注册账号

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "myuser@example.com",
    "password": "mypassword123"
  }'
```

### 2. 登录获取Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypassword123"
  }'
```

保存返回的 `access_token`，后续请求需要用到。

### 3. 上传文档

创建一个测试文件 `test.txt`:
```
这是一篇关于人工智能的文章。
人工智能技术正在改变世界，深度学习是其中的核心技术。
```

上传文档：
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.txt" \
  -F "category=科技"
```

### 4. 语义检索

```bash
curl -X POST http://localhost:5000/api/search/semantic \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能技术",
    "k": 10
  }'
```

### 5. 查看统计信息

```bash
curl -X GET http://localhost:5000/api/analysis/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🎯 常用操作

### 获取文档列表

```bash
curl -X GET "http://localhost:5000/api/documents/?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 按分类筛选

```bash
curl -X GET "http://localhost:5000/api/documents/?category=科技" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 按时间范围筛选

```bash
curl -X GET "http://localhost:5000/api/documents/?time_range=7days" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 更新文档

```bash
curl -X PUT http://localhost:5000/api/documents/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的标题",
    "category": "新分类",
    "tags": ["标签1", "标签2"]
  }'
```

### 删除文档

```bash
curl -X DELETE http://localhost:5000/api/documents/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 批量删除

```bash
curl -X POST http://localhost:5000/api/documents/batch-delete \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3]
  }'
```

### 联网搜索

```bash
curl -X POST http://localhost:5000/api/search/web \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "最新科技新闻",
    "num_results": 3
  }'
```

### 组合搜索（智能选择）

```bash
curl -X POST http://localhost:5000/api/search/combined \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "量子计算发展",
    "k": 10
  }'
```

### 提取关键词

```bash
curl -X POST http://localhost:5000/api/analysis/keywords \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "7days",
    "topK": 10
  }'
```

### 获取分析报告

```bash
curl -X GET "http://localhost:5000/api/analysis/report?time_range=30days" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🐛 故障排查

### 服务无法启动

1. 检查端口是否被占用：
   ```bash
   # Linux/Mac
   lsof -i :5000
   # Windows
   netstat -ano | findstr :5000
   ```

2. 检查Python版本：
   ```bash
   python --version  # 需要 3.8+
   ```

### Token过期

重新登录获取新Token，或使用刷新Token：

```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### 向量检索异常

删除并重建索引：

```bash
rm -rf faiss_index/
python app.py  # 重启服务
```

### 文件上传失败

检查文件大小限制 (默认50MB)：

```python
# config.py
MAX_UPLOAD_SIZE = 52428800  # 调整大小
```

## 📚 下一步

- 查看完整 [API文档](README.md#api文档)
- 运行 [测试套件](README.md#测试)
- 阅读 [部署指南](README.md#部署)
- 配置 [Ollama](README.md#ollama连接失败) 启用LLM功能

## 💡 提示

- 首次搜索会较慢，因为需要加载嵌入模型
- 建议在生产环境使用PostgreSQL替代SQLite
- 使用Gunicorn部署以提高性能
- 定期备份数据库和FAISS索引文件

---

**有问题？** 查看 [常见问题](README.md#常见问题) 或提交Issue。


