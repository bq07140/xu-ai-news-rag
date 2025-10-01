# 🚀 n8n Integration - Simple Setup (No Authentication Required)

## ✨ One Minute Configuration

Your n8n workflow only needs one **HTTP Request** node to store data into the project database!

---

## 📝 Configuration Steps

### In Your n8n Workflow

Add an **HTTP Request** node at the end of your workflow (after the Markdown node):

---

## ⚙️ HTTP Request Node Configuration

### Basic Settings

| Option | Value |
|--------|-------|
| **Method** | `POST` |
| **URL** | `http://localhost:5000/api/documents/webhook/n8n` |

### Authentication

**✅ None** - No authentication required!

### Body

| Option | Value |
|--------|-------|
| **Body Content Type** | `JSON` |

### Body (JSON)

```json
{
  "title": "{{ $json.title }}",
  "content": "{{ $json.content }}",
  "summary": "{{ $json.summary }}",
  "category": "{{ $json.category || 'News' }}",
  "source": "n8n Auto-crawl",
  "source_url": "{{ $json.link }}",
  "tags": {{ $json.tags || [] }},
  "author": "{{ $json.author }}"
}
```

---

## 🎯 That's It!

After configuration:
1. ✅ Click n8n's "Execute Workflow" button
2. ✅ Check the HTTP Request node's response
3. ✅ Open browser and visit http://localhost:3000/documents
4. ✅ View the auto-crawled news

---

## 📋 Complete Workflow Diagram

```
┌─────────────────┐
│ Schedule Trigger│  Timed trigger (e.g., every hour)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RSS Read      │  Read RSS feed
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Limit       │  Limit quantity (e.g., 10 items)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scrape URL     │  Scrape full content
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │  Generate summary and category
│  (DeepSeek)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Aggregate     │  Aggregate data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Markdown      │  Format
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ HTTP Request    │  ← Add here!
│  (POST Webhook) │     No authentication needed
└─────────────────┘
```

---

## 📊 Field Mapping

| n8n Variable | API Field | Required | Description |
|--------------|-----------|----------|-------------|
| `{{ $json.title }}` | `title` | ✅ Required | News title |
| `{{ $json.content }}` | `content` | ✅ Required | Full content |
| `{{ $json.summary }}` | `summary` | Optional | AI-generated summary |
| `{{ $json.category }}` | `category` | Optional | Category (default: News) |
| `{{ $json.link }}` | `source_url` | Optional | Original link |
| `{{ $json.tags }}` | `tags` | Optional | Tags array |
| `{{ $json.author }}` | `author` | Optional | Author |

---

## 🧪 Testing

### Test Single Data

Use Postman or curl:

```bash
curl -X POST http://localhost:5000/api/documents/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test News Title",
    "content": "This is the complete content of the test news...",
    "category": "Technology",
    "source": "n8n test"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully created 1 document",
  "count": 1,
  "documents": [...]
}
```

---

## 🎨 Advanced Configuration (Optional)

### 1. Add Error Handling

Add an **IF** node after the HTTP Request node:

```
Condition: {{ $json.success }} === true
True ✅: Continue
False ❌: Send error notification
```

### 2. Data Formatting (Function Node)

If your data format is different, add a **Function** node before HTTP Request:

```javascript
// Format data
const items = [];

for (const item of $input.all()) {
  const data = item.json;
  
  // Auto-categorize
  let category = 'News';
  const text = (data.title + ' ' + data.content).toLowerCase();
  
  if (text.includes('ai') || text.includes('tech')) {
    category = 'Technology';
  } else if (text.includes('economy') || text.includes('stock')) {
    category = 'Finance';
  } else if (text.includes('football') || text.includes('game')) {
    category = 'Sports';
  }
  
  items.push({
    json: {
      title: data.title || 'Untitled',
      content: data.content || data.description || '',
      summary: data.summary || data.description?.substring(0, 200) || '',
      category: category,
      source: 'n8n RSS Subscribe',
      source_url: data.link || '',
      tags: data.tags || [],
      author: data.author || ''
    }
  });
}

return items;
```

### 3. Batch Send (Optional)

If RSS returns multiple news items, send them all at once:

**Body configuration:**
```json
{{ JSON.stringify($input.all().map(item => ({
  title: item.json.title,
  content: item.json.content,
  summary: item.json.summary,
  category: item.json.category || 'News',
  source: 'n8n Auto-crawl',
  source_url: item.json.link,
  tags: item.json.tags || [],
  author: item.json.author
}))) }}
```

---

## ✅ Verify Results

### Method 1: Frontend View

Open browser: http://localhost:3000/documents

You should see the auto-crawled news!

### Method 2: Backend Logs

Check backend terminal, should display:

```
127.0.0.1 - - [01/Oct/2025 15:XX:XX] "POST /api/documents/webhook/n8n HTTP/1.1" 201 -
```

Status code `201` means success!

### Method 3: API Query

```bash
# Get latest document list
curl http://localhost:5000/api/documents/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Missing required fields | Ensure `title` and `content` are present |
| 500 Server Error | Backend error | Check backend logs |
| Connection timeout | Backend not running | Confirm service on port 5000 |
| Data not showing | User ID mismatch | Log in to frontend with bq07140@gmail.com |

---

## 📖 API Endpoint Documentation

### Webhook Endpoint

**URL:** `http://localhost:5000/api/documents/webhook/n8n`

**Method:** `POST`

**Authentication:** No authentication required (auto-linked to your account)

**Request Body:**
```json
{
  "title": "News Title (required)",
  "content": "News Content (required)",
  "summary": "Summary (optional)",
  "category": "Category (optional, default: News)",
  "source": "Source (optional, default: n8n Auto-crawl)",
  "source_url": "Original Link (optional)",
  "tags": ["Tag1", "Tag2"],
  "author": "Author (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully created 1 document",
  "count": 1,
  "documents": [
    {
      "id": 10,
      "title": "News Title",
      "category": "Technology",
      ...
    }
  ]
}
```

---

## 💡 Recommended Workflow Configuration

### Recommended RSS Feeds

- **Tech News**: 
  - TechCrunch: https://techcrunch.com/feed/
  - Hacker News: https://news.ycombinator.com/rss
  
- **Finance News**:
  - Bloomberg: https://www.bloomberg.com/feed/
  - Financial Times: https://www.ft.com/rss/home

### AI Agent Prompt

```
Please analyze the following news content and provide:
1. One-sentence summary (no more than 100 words)
2. Category (choose from: Technology/Finance/Sports/Health/Entertainment/Other)
3. 3-5 keyword tags

News Title: {{ $json.title }}
News Content: {{ $json.content.substring(0, 500) }}

Please return in JSON format:
{
  "summary": "summary text",
  "category": "category",
  "tags": ["tag1", "tag2", "tag3"]
}
```

---

## 🎉 Done!

Now your n8n workflow can automatically:
1. ✅ Crawl news from RSS
2. ✅ Use AI to generate summaries and categories
3. ✅ Auto-save to project database
4. ✅ Auto-vectorize for semantic search support
5. ✅ View in real-time on frontend

---

**Need help?** Check complete documentation: `backend/API_EXAMPLES.md`

Happy using! 🚀
