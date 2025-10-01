# API使用示例集合

完整的API调用示例，包含Python、JavaScript和cURL版本。

## 目录

- [认证相关](#认证相关)
- [文档管理](#文档管理)
- [搜索功能](#搜索功能)
- [数据分析](#数据分析)

---

## 认证相关

### 用户注册

**cURL:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

**Python:**
```python
import requests

url = "http://localhost:5000/api/auth/register"
data = {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
}
response = requests.post(url, json=data)
print(response.json())
```

**JavaScript:**
```javascript
fetch('http://localhost:5000/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'password123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### 用户登录

**Python完整示例:**
```python
import requests

class NewsRAGClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
        
    def login(self, username, password):
        """用户登录"""
        url = f"{self.base_url}/api/auth/login"
        data = {"username": username, "password": password}
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            print(f"✓ 登录成功: {username}")
            return True
        else:
            print(f"✗ 登录失败: {response.json()}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

# 使用示例
client = NewsRAGClient()
client.login("myuser", "mypassword123")
```

---

## 文档管理

### 上传文档

**Python完整示例:**
```python
def upload_document(client, file_path, category="未分类"):
    """上传文档"""
    url = f"{client.base_url}/api/documents/upload"
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'category': category}
        headers = {'Authorization': f'Bearer {client.access_token}'}
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
    if response.status_code == 201:
        doc = response.json()['document']
        print(f"✓ 上传成功: {doc['title']} (ID: {doc['id']})")
        return doc
    else:
        print(f"✗ 上传失败: {response.json()}")
        return None

# 使用示例
upload_document(client, "test.pdf", "科技")
```

### 批量上传文档

**Python:**
```python
import os
from pathlib import Path

def batch_upload_documents(client, folder_path, category="未分类"):
    """批量上传文件夹中的所有文档"""
    supported_formats = ['.pdf', '.docx', '.txt', '.xlsx', '.md']
    uploaded = []
    
    for file_path in Path(folder_path).rglob('*'):
        if file_path.suffix.lower() in supported_formats:
            doc = upload_document(client, str(file_path), category)
            if doc:
                uploaded.append(doc)
    
    print(f"\n✓ 批量上传完成: {len(uploaded)}/{len(list(Path(folder_path).rglob('*')))} 个文件")
    return uploaded

# 使用示例
batch_upload_documents(client, "./documents/tech_news", "科技")
```

### 获取文档列表（带筛选）

**Python:**
```python
def get_documents(client, category=None, time_range=None, page=1, per_page=20):
    """获取文档列表"""
    url = f"{client.base_url}/api/documents/"
    params = {'page': page, 'per_page': per_page}
    
    if category:
        params['category'] = category
    if time_range:
        params['time_range'] = time_range
    
    response = requests.get(url, headers=client.get_headers(), params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取文档: {data['total']} 条")
        return data['documents']
    return []

# 使用示例
docs = get_documents(client, category="科技", time_range="7days")
for doc in docs:
    print(f"  - {doc['title']} ({doc['created_at']})")
```

### 更新文档元数据

**Python:**
```python
def update_document(client, doc_id, **kwargs):
    """更新文档元数据"""
    url = f"{client.base_url}/api/documents/{doc_id}"
    response = requests.put(url, headers=client.get_headers(), json=kwargs)
    
    if response.status_code == 200:
        doc = response.json()['document']
        print(f"✓ 更新成功: {doc['title']}")
        return doc
    else:
        print(f"✗ 更新失败: {response.json()}")
        return None

# 使用示例
update_document(client, 1, 
    title="更新后的标题",
    category="科技",
    tags=["AI", "机器学习", "深度学习"],
    notes="这是一篇重要的文章"
)
```

### 批量删除文档

**Python:**
```python
def batch_delete_documents(client, doc_ids):
    """批量删除文档"""
    url = f"{client.base_url}/api/documents/batch-delete"
    data = {'ids': doc_ids}
    response = requests.post(url, headers=client.get_headers(), json=data)
    
    if response.status_code == 200:
        count = response.json()['deleted_count']
        print(f"✓ 删除成功: {count} 个文档")
        return True
    return False

# 使用示例
batch_delete_documents(client, [1, 2, 3, 4, 5])
```

---

## 搜索功能

### 语义检索

**Python完整示例:**
```python
def semantic_search(client, query, k=10, threshold=0.6):
    """语义检索"""
    url = f"{client.base_url}/api/search/semantic"
    data = {
        'query': query,
        'k': k,
        'threshold': threshold
    }
    response = requests.post(url, headers=client.get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 搜索完成: 找到 {result['count']} 条结果")
        
        for i, doc in enumerate(result['results'], 1):
            print(f"\n{i}. {doc['title']}")
            print(f"   相似度: {doc['similarity']:.2%}")
            print(f"   分类: {doc['category']} | 来源: {doc['source']}")
            print(f"   摘要: {doc['summary'][:100]}...")
        
        return result['results']
    return []

# 使用示例
results = semantic_search(client, "人工智能最新进展", k=5)
```

### 智能组合搜索

**Python:**
```python
def smart_search(client, query):
    """智能组合搜索（自动决定是否联网）"""
    url = f"{client.base_url}/api/search/combined"
    data = {'query': query}
    response = requests.post(url, headers=client.get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        # 显示知识库结果
        kb_results = result['knowledge_base_results']
        print(f"\n📚 知识库结果: {len(kb_results)} 条")
        for doc in kb_results[:3]:
            print(f"  • {doc['title']} (相似度: {doc['similarity']:.2%})")
        
        # 显示网络搜索结果
        if result['web_search_triggered']:
            print(f"\n🌐 网络搜索结果:")
            print(f"  {result['web_summary']}")
        
        return result
    return None

# 使用示例
smart_search(client, "今天量子计算领域的最新消息")
```

### 搜索历史

**Python:**
```python
def get_search_history(client, limit=10):
    """获取搜索历史"""
    url = f"{client.base_url}/api/search/history"
    params = {'limit': limit}
    response = requests.get(url, headers=client.get_headers(), params=params)
    
    if response.status_code == 200:
        history = response.json()['history']
        print(f"✓ 搜索历史: {len(history)} 条")
        
        for i, item in enumerate(history, 1):
            print(f"{i}. {item['query']}")
            print(f"   结果数: {item['result_count']} | 类型: {item['search_type']}")
            print(f"   时间: {item['created_at']}")
        
        return history
    return []

# 使用示例
get_search_history(client, limit=10)
```

---

## 数据分析

### 获取统计信息

**Python:**
```python
def get_statistics(client):
    """获取统计信息"""
    url = f"{client.base_url}/api/analysis/stats"
    response = requests.get(url, headers=client.get_headers())
    
    if response.status_code == 200:
        stats = response.json()
        print("\n📊 知识库统计:")
        print(f"  总文档数: {stats['total_documents']}")
        print(f"  近7天新增: {stats['recent_7days']}")
        print(f"  向量索引大小: {stats['index_size']}")
        
        print("\n  分类分布:")
        for category, count in stats['category_distribution'].items():
            print(f"    • {category}: {count}")
        
        print("\n  来源分布:")
        for source, count in stats['source_distribution'].items():
            print(f"    • {source}: {count}")
        
        return stats
    return None

# 使用示例
get_statistics(client)
```

### 提取关键词

**Python:**
```python
def extract_keywords(client, time_range='7days', topK=10, category=None):
    """提取关键词"""
    url = f"{client.base_url}/api/analysis/keywords"
    data = {
        'time_range': time_range,
        'topK': topK
    }
    if category:
        data['category'] = category
    
    response = requests.post(url, headers=client.get_headers(), json=data)
    
    if response.status_code == 200:
        result = response.json()
        keywords = result['keywords']
        
        print(f"\n🔑 Top {topK} 关键词 (基于 {result['document_count']} 个文档):")
        for i, kw in enumerate(keywords, 1):
            print(f"{i}. {kw['keyword']}")
            print(f"   出现次数: {kw['count']} | 权重: {kw['weight']:.4f}")
        
        return keywords
    return []

# 使用示例
extract_keywords(client, time_range='30days', topK=10)
```

### 生成综合分析报告

**Python:**
```python
def generate_report(client, time_range='7days'):
    """生成综合分析报告"""
    url = f"{client.base_url}/api/analysis/report"
    params = {'time_range': time_range}
    response = requests.get(url, headers=client.get_headers(), params=params)
    
    if response.status_code == 200:
        report = response.json()['report']
        
        print("\n" + "="*50)
        print(f"  知识库分析报告 ({time_range})")
        print("="*50)
        
        print(f"\n📈 基本信息:")
        print(f"  文档总数: {report['total_documents']}")
        print(f"  生成时间: {report['generated_at']}")
        
        print(f"\n🔑 Top 10 关键词:")
        for i, kw in enumerate(report['top_keywords'][:10], 1):
            print(f"  {i}. {kw['keyword']} (权重: {kw['weight']:.4f})")
        
        print(f"\n📊 分类分布:")
        for category, count in report['category_distribution'].items():
            percentage = (count / report['total_documents']) * 100
            print(f"  • {category}: {count} ({percentage:.1f}%)")
        
        if 'time_trend' in report:
            print(f"\n📅 时间趋势:")
            for date, count in sorted(report['time_trend'].items()):
                print(f"  {date}: {count} 篇")
        
        print("\n" + "="*50)
        return report
    
    elif response.status_code == 400:
        error = response.json()
        print(f"⚠ {error['message']} (当前: {error['current_count']} 条)")
    
    return None

# 使用示例
generate_report(client, time_range='30days')
```

---

## 完整工作流示例

```python
#!/usr/bin/env python3
"""
完整的工作流示例
"""

import requests
from pathlib import Path

class NewsRAGClient:
    """XU-News-AI-RAG 客户端"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
    
    # ... (包含上面所有方法) ...

def main():
    """主工作流"""
    
    # 1. 初始化客户端
    client = NewsRAGClient("http://localhost:5000")
    
    # 2. 注册和登录
    print("\n=== 用户认证 ===")
    client.login("myuser", "mypassword123")
    
    # 3. 上传文档
    print("\n=== 上传文档 ===")
    batch_upload_documents(client, "./news_articles", "科技")
    
    # 4. 查看统计
    print("\n=== 统计信息 ===")
    get_statistics(client)
    
    # 5. 语义检索
    print("\n=== 语义检索 ===")
    results = semantic_search(client, "人工智能和机器学习", k=5)
    
    # 6. 智能搜索
    print("\n=== 智能搜索 ===")
    smart_search(client, "最新的量子计算突破")
    
    # 7. 数据分析
    print("\n=== 数据分析 ===")
    extract_keywords(client, time_range='7days', topK=10)
    generate_report(client, time_range='7days')
    
    # 8. 文档管理
    print("\n=== 文档管理 ===")
    docs = get_documents(client, category="科技", time_range="7days")
    if docs:
        # 更新第一个文档
        update_document(client, docs[0]['id'], 
            tags=["重要", "AI", "深度学习"])
    
    print("\n✓ 工作流完成!")

if __name__ == "__main__":
    main()
```

---

## 错误处理示例

```python
def safe_api_call(func):
    """API调用装饰器，统一错误处理"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            print("✗ 连接错误: 无法连接到服务器")
        except requests.exceptions.Timeout:
            print("✗ 超时错误: 请求超时")
        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP错误: {e}")
        except Exception as e:
            print(f"✗ 未知错误: {e}")
        return None
    return wrapper

@safe_api_call
def safe_search(client, query):
    """带错误处理的搜索"""
    return semantic_search(client, query)

# 使用示例
result = safe_search(client, "测试查询")
```

---

更多示例和最佳实践，请参考 [README.md](README.md)


