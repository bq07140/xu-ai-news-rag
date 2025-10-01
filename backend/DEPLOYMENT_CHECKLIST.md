# 部署检查清单

在将应用部署到生产环境前，请按此清单逐项检查。

## ✅ 部署前检查

### 🔧 环境配置

- [ ] 设置 `FLASK_ENV=production`
- [ ] 生成强随机密钥
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] 更新 `SECRET_KEY` (32字节以上)
- [ ] 更新 `JWT_SECRET_KEY` (32字节以上)
- [ ] 配置生产数据库URI（PostgreSQL推荐）
- [ ] 检查文件上传大小限制
- [ ] 配置CORS允许的域名

### 🗄️ 数据库

- [ ] 备份开发环境数据（如需要）
- [ ] 创建生产数据库
- [ ] 运行数据库迁移
  ```bash
  python app.py  # 自动创建表
  ```
- [ ] 验证表结构正确
- [ ] 配置数据库连接池
- [ ] 设置定期备份任务

### 🔐 安全配置

- [ ] 禁用DEBUG模式 (`FLASK_ENV=production`)
- [ ] 配置HTTPS（生产环境必须）
- [ ] 设置防火墙规则
- [ ] 配置API速率限制（推荐）
- [ ] 检查文件权限（数据库、上传目录）
- [ ] 配置安全响应头
- [ ] 设置CSRF保护（如有前端）

### 📦 依赖和资源

- [ ] 安装所有生产依赖
  ```bash
  pip install -r requirements.txt
  ```
- [ ] 下载嵌入模型（all-MiniLM-L6-v2）
- [ ] 创建必要目录
  ```bash
  mkdir -p uploads faiss_index logs
  ```
- [ ] 配置日志轮转
- [ ] 检查磁盘空间（推荐至少10GB）
- [ ] 安装Gunicorn
  ```bash
  pip install gunicorn
  ```

### 🚀 服务器配置

- [ ] 选择服务器方案：
  - [ ] Gunicorn + Nginx
  - [ ] Docker容器
  - [ ] 云服务（AWS/Azure/GCP）
- [ ] 配置反向代理（Nginx推荐）
- [ ] 配置负载均衡（如有多实例）
- [ ] 设置进程管理（systemd/supervisor）
- [ ] 配置自动重启

### 🔍 监控和日志

- [ ] 配置应用日志
- [ ] 配置错误日志
- [ ] 设置日志级别（INFO或WARNING）
- [ ] 配置日志存储路径
- [ ] 设置监控告警（可选）
- [ ] 配置性能监控（可选）

### 🧪 测试

- [ ] 运行所有单元测试
  ```bash
  pytest
  ```
- [ ] 运行集成测试
  ```bash
  python test_api.py
  ```
- [ ] 测试生产配置下的启动
- [ ] 测试所有关键API端点
- [ ] 压力测试（可选）

## 📝 生产环境配置示例

### Nginx配置

创建 `/etc/nginx/sites-available/xu-news-rag`:

```nginx
upstream xu_news_rag {
    server 127.0.0.1:5000;
    # 如有多实例
    # server 127.0.0.1:5001;
    # server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 文件上传大小限制
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://xu_news_rag;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件（如有）
    location /static/ {
        alias /path/to/backend/static/;
        expires 30d;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/xu-news-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd服务配置

创建 `/etc/systemd/system/xu-news-rag.service`:

```ini
[Unit]
Description=XU News RAG Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 60 \
    --access-logfile /var/log/xu-news-rag/access.log \
    --error-logfile /var/log/xu-news-rag/error.log \
    --log-level info \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable xu-news-rag
sudo systemctl start xu-news-rag
sudo systemctl status xu-news-rag
```

### Docker部署

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p uploads faiss_index logs

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "60", "app:app"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URI=postgresql://user:pass@db:5432/xu_news_rag
    volumes:
      - ./uploads:/app/uploads
      - ./faiss_index:/app/faiss_index
      - ./logs:/app/logs
    depends_on:
      - db
    restart: always
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=xu_news_rag
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

部署：
```bash
docker-compose up -d
```

### 环境变量文件 (.env)

生产环境 `.env` 示例：

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-32-bytes-minimum
PORT=5000

# JWT
JWT_SECRET_KEY=your-production-jwt-secret-key-32-bytes

# Database
DATABASE_URI=postgresql://dbuser:dbpass@localhost:5432/xu_news_rag

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Search API
SEARCH_API_KEY=your-baidu-api-key
SEARCH_API_URL=https://api.baidu.com/search

# Configuration
SIMILARITY_THRESHOLD=0.6
MAX_SEARCH_RESULTS=10
MAX_UPLOAD_SIZE=52428800

# Paths
UPLOAD_FOLDER=/var/lib/xu-news-rag/uploads
FAISS_INDEX_PATH=/var/lib/xu-news-rag/faiss_index
```

## 🚨 部署后验证

### 基础功能验证

```bash
# 1. 健康检查
curl https://your-domain.com/health

# 2. 注册用户
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpass123"}'

# 3. 登录
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"testpass123"}'

# 4. 上传文档（需要token）
curl -X POST https://your-domain.com/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt"

# 5. 搜索测试
curl -X POST https://your-domain.com/api/search/semantic \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"测试查询"}'
```

### 性能验证

```bash
# 使用ab进行压力测试
ab -n 1000 -c 10 https://your-domain.com/health

# 使用wrk进行负载测试
wrk -t4 -c100 -d30s https://your-domain.com/health
```

### 监控检查

- [ ] 检查应用日志
  ```bash
  tail -f /var/log/xu-news-rag/error.log
  ```
- [ ] 检查系统资源使用
  ```bash
  htop
  df -h
  ```
- [ ] 检查数据库连接
- [ ] 检查FAISS索引文件

## 🔄 维护任务

### 日常维护

- [ ] 每日检查日志文件
- [ ] 监控磁盘空间使用
- [ ] 监控数据库性能
- [ ] 检查错误率

### 定期维护

- [ ] 每周数据库备份验证
- [ ] 每月检查和更新依赖包
- [ ] 每季度安全审计
- [ ] 每半年性能优化评估

### 备份策略

```bash
# 数据库备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/xu-news-rag

# 备份SQLite（如使用）
cp /path/to/xu_news_rag.db $BACKUP_DIR/db_$DATE.db

# 备份PostgreSQL（如使用）
pg_dump xu_news_rag > $BACKUP_DIR/db_$DATE.sql

# 备份FAISS索引
tar -czf $BACKUP_DIR/faiss_$DATE.tar.gz /path/to/faiss_index/

# 删除30天前的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

配置cron定时任务：
```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 📊 监控指标

### 关键指标

- **响应时间**: P50, P95, P99
- **错误率**: 4xx, 5xx错误比例
- **请求量**: QPS
- **数据库**: 连接数、查询时间
- **系统资源**: CPU、内存、磁盘
- **向量检索**: 检索时间、索引大小

### 告警阈值建议

- 响应时间 P95 > 2秒
- 错误率 > 1%
- CPU使用率 > 80%
- 内存使用率 > 85%
- 磁盘使用率 > 90%
- 数据库连接数 > 80%池大小

## 🆘 故障处理

### 常见问题

1. **服务无响应**
   - 检查进程是否运行
   - 检查端口是否被占用
   - 查看错误日志
   - 重启服务

2. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串
   - 检查防火墙规则
   - 增加连接池大小

3. **向量检索失败**
   - 检查FAISS索引文件完整性
   - 重建索引
   - 检查模型文件

4. **内存不足**
   - 减少worker数量
   - 增加系统内存
   - 优化批处理大小

### 紧急回滚

```bash
# 停止服务
sudo systemctl stop xu-news-rag

# 恢复数据库
psql xu_news_rag < /backups/db_backup.sql

# 恢复FAISS索引
tar -xzf /backups/faiss_backup.tar.gz -C /

# 回滚代码（如使用Git）
git checkout previous-stable-tag
pip install -r requirements.txt

# 启动服务
sudo systemctl start xu-news-rag
```

## 📞 支持联系

- **技术支持**: support@xu-news-rag.com
- **紧急联系**: +86-xxx-xxxx-xxxx
- **文档**: https://docs.xu-news-rag.com

---

**最后更新**: 2025-10-01  
**版本**: v1.0.0


