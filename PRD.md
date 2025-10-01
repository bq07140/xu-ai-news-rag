# XU-News-AI-RAG User-Facing Module PRD

## 1. Introduction

### 1.1 Background
With the advent of the information explosion era, users face challenges in filtering and managing massive amounts of news information. The XU-News-AI-RAG system has completed its basic architecture (scheduled crawling, model deployment, knowledge base construction, data storage, email notifications). Now we need to build a user-facing interface that enables users to efficiently manage their personal news knowledge base and obtain precise information through AI-enhanced semantic retrieval.

### 1.2 Target Users
- **Primary Users**: Professionals who need to continuously track news in specific domains (researchers, analysts, journalists, investors, etc.)
- **Secondary Users**: Knowledge workers with in-depth information needs on specific topics
- **User Characteristics**:
  - Basic internet operation skills
  - Need to quickly retrieve and manage large amounts of news information
  - Want to improve information acquisition efficiency through intelligent means

### 1.3 Product Vision
Create an intelligent personalized news knowledge base system that allows users to easily manage massive news data, quickly obtain needed information through AI-driven semantic retrieval, gain insights into news hotspots and trends through data analysis, and become users' intelligent news assistant.

---

## 2. User Stories and Scenario Descriptions

### User Story 1: Secure Login
**As** a user, **I want to** log in to the system with username and password, **so that** I can securely access my personal news knowledge base.

**Scenario Description**:
Li, a financial analyst, opens the browser every morning, accesses the XU-News-AI-RAG system, enters username and password to log in, and enters the personal workspace to view the latest collected financial news.

### User Story 2: Knowledge Base Content Management
**As** a user, **I want to** view, filter, edit, and delete news data in the knowledge base, **so that** I can keep the knowledge base clean and relevant.

**Scenario Description**:
- **View & Filter**: After logging in, Li sees the data list, filters by "Technology" and "Last 7 days", quickly browses relevant news titles and summaries.
- **Delete Operation**: Finds several outdated or irrelevant news items, selects and batch deletes them.
- **Edit Metadata**: Adds tag "Key Focus" to an important news item and modifies source attribution.
- **Upload Data**: Receives an industry report PDF, uploads it to the knowledge base through the page upload function.

### User Story 3: Intelligent Semantic Search
**As** a user, **I want to** retrieve the knowledge base through natural language questions, **so that** I can quickly find news content related to the question.

**Scenario Description**:
Li enters "What major breakthroughs in AI recently?" in the search box. The system retrieves the top 5 most relevant news items from the knowledge base, displays them sorted by similarity, and highlights key information.

### User Story 4: Intelligent Web Search Supplement
**As** a user, **I want** the system to automatically search the web when the knowledge base has no relevant content, **so that** I can get more comprehensive information.

**Scenario Description**:
Li asks "Latest news on quantum computing today". The knowledge base currently has no relevant content. The system automatically calls the Baidu Search API, retrieves the top 3 latest results, processes them through a large language model, and presents them to the user in a friendly manner.

### User Story 5: Data Insights and Analysis
**As** a user, **I want to** view clustering analysis reports of the knowledge base, **so that** I can understand current news hotspots and topic distribution.

**Scenario Description**:
Li clicks the "Data Analysis" menu to view the Top 10 keyword distribution chart for this week's knowledge base, discovers that keywords like "chips" and "autonomous driving" are rising in popularity, and adjusts subsequent information focus accordingly.

---

## 3. Product Scope and Feature List

### 3.1 Core Features

#### Feature 1: User Authentication System
- **Feature ID**: F-AUTH-001
- **Priority**: P0 (Must-have)
- **Feature Description**:
  - User registration (username, email, password)
  - User login (supports session persistence)
  - Password encryption storage (using bcrypt or similar algorithms)
  - Login status verification (based on Token or Session)
  - Logout functionality

#### Feature 2: Knowledge Base Content Management
- **Feature ID**: F-KB-001
- **Priority**: P0 (Must-have)
- **Feature Description**:
  
  **2.1 Data List Display**
  - Display fields: title, summary, source, type, timestamp, tags
  - Paginated display (default 20 items per page)
  - Support sorting (by time, relevance)
  
  **2.2 Filtering Features**
  - Filter by type (e.g., Technology, Finance, Sports, etc.)
  - Filter by time range (today, last 7 days, last 30 days, custom interval)
  - Filter by source (RSS, web scraping, manual upload)
  - Filter by tags
  
  **2.3 Delete Operations**
  - Single deletion (with confirmation)
  - Batch deletion (checkboxes + batch operation button)
  - Auto-refresh list after deletion
  
  **2.4 Metadata Editing**
  - Edit tags (support adding, removing tags)
  - Modify source attribution
  - Edit category type
  - Add notes
  
  **2.5 Data Upload**
  - Supported file types: PDF, DOCX, TXT, Excel (XLSX/XLS), Markdown
  - Single file upload (max 50MB)
  - Batch upload (max 10 files)
  - Upload progress display
  - Auto-parse and store after upload
  - Upload failure alerts and error logs

#### Feature 3: Intelligent Search (Based on SQLite Full-Text Search)
- **Feature ID**: F-SEARCH-001
- **Priority**: P0 (Must-have)
- **Feature Description**:
  - Natural language input box (supports multi-line text)
  - Full-text search:
    - Uses SQLite FTS5 (Full-Text Search extension)
    - Keyword matching in title and content fields
    - Supports Chinese word segmentation and fuzzy matching
    - Supports AND/OR logical operators
  - Result sorting:
    - Sort by keyword match score
    - Sort by time descending (optional)
  - Result display:
    - Highlight matched keywords
    - Display news title, summary, source, time
    - Display matched snippet preview
    - Support click to view full content
  - Search history (stored in SQLite, last 10 searches)
  - Search modes:
    - Title search: search title field only
    - Full-text search: search title and content
    - Web search: network search only (optional)
    - Smart combined: prioritize local, supplement with web results if insufficient

#### Feature 4: Intelligent Web Query
- **Feature ID**: F-WEB-001
- **Priority**: P1 (Important)
- **Feature Description**:
  - Trigger condition: knowledge base search results < 3 or similarity below threshold
  - Call Baidu Search API (or other search engine APIs)
  - Retrieve top 3 web search results
  - Process through large language model:
    - Extract key information
    - Generate structured summary
    - Analyze relevance to user question
  - Result display:
    - Clearly marked as "Web Search Results"
    - Display source links
    - Show AI-generated summary
  - Optional: save web search results to knowledge base

#### Feature 5: Data Clustering Analysis
- **Feature ID**: F-ANALYSIS-001
- **Priority**: P1 (Important)
- **Feature Description**:
  - Keyword extraction (TF-IDF or TextRank algorithm)
  - Top 10 keyword statistics and ranking
  - Visualization:
    - Bar chart (keyword frequency)
    - Word cloud (optional)
    - Time trend chart (keyword popularity changes)
  - Time range selection (last 7 days, last 30 days, all)
  - Category dimension analysis (statistics by news type)
  - Data export (PNG, Excel)

---

## 4. Product-Specific AI Requirements

### 4.1 Model Requirements

#### 4.1.1 Chinese Word Segmentation Tool
- **Tool**: jieba library
- **Usage**:
  - Chinese word segmentation for search queries
  - Keyword extraction (TF-IDF / TextRank)
  - Keyword statistics in data analysis
- **Performance Metrics**:
  - Segmentation speed: > 1MB/s
  - Accuracy: > 90%

#### 4.1.2 Large Language Model (LLM) - Optional
- **Model**: qwen2.5:3b (deployed via Ollama)
- **Usage**:
  - Understanding and summary generation of web search results
  - Secondary understanding and integration of search results
  - Generate user-friendly answers
- **Performance Metrics**:
  - Response time: < 3 seconds (single inference)
  - Output quality: fluent, accurate, contextually appropriate
  - Concurrency: supports at least 5 concurrent requests

### 4.2 Data Requirements

#### 4.2.1 Data Sources
- Existing knowledge base data (from steps 1-5 auto-crawling)
- User manually uploaded documents
- Supplementary data from web queries

#### 4.2.2 Data Scale
- Initial scale: 1,000-10,000 news items
- Growth rate: 50-200 new items per day
- Full-text indexing: based on SQLite FTS5, supports 10,000+ documents
- Data storage: SQLite database (single file, easy to backup and migrate)
- Index size: typically 30-50% of data size

#### 4.2.3 Data Quality
- Text cleaning: remove HTML tags, special characters, advertising content
- Deduplication: content similarity-based deduplication (similarity >0.95 considered duplicate)
- Completeness check: title, content, timestamp are required fields

#### 4.2.4 Data Annotation
- Category tags: auto-classification (based on keywords or simple model) + user manual correction
- Metadata: source, time, author, original URL
- User tags: user-defined tag system

### 4.3 Algorithm Boundaries and Explainability

#### 4.3.1 Algorithm Boundaries
- **Full-text search boundaries**:
  - Keyword matching: at least 1 keyword match
  - Search result limit: return Top 20 results
  - No results: prompt user to adjust keywords or try web search
  - Support wildcard search (e.g., AI*)
  
- **Web query boundaries**:
  - Only triggered when knowledge base has no results or < 3 results
  - Limit to max 3 web results per query
  - Prioritize triggering for time-sensitive questions (containing "today", "latest", etc.)

- **Clustering analysis boundaries**:
  - Only analyze structured data already in database
  - Minimum data volume: at least 100 items to generate report
  - Keyword extraction: for Chinese content only

#### 4.3.2 Explainability
- **Search result explainability**:
  - Display number of matched keywords
  - Highlight matched keywords or phrases
  - Display matched snippet preview
  - Sort by time or relevance (user selectable)
  
- **Web query prompts**:
  - Clearly inform user that current results are from web search
  - Explain reason for triggering web query (e.g., "No relevant content in knowledge base")
  
- **Analysis report explanation**:
  - Explain time range and data volume for keyword extraction
  - Provide brief explanation of analysis method

### 4.4 Evaluation Criteria

#### 4.4.1 Search Quality Evaluation (Based on SQLite Full-Text Search)
- **Precision@K**: Proportion of relevant results in Top 10 > 60%
- **Recall**: Proportion of relevant documents retrieved > 60%
- **Query response rate**: 90% of queries return at least 1 result
- **User satisfaction**: Collect feedback through "Helpful"/"Not helpful" buttons, satisfaction > 75%

#### 4.4.2 Performance Evaluation
- **Full-text search response time**: P95 < 1 second
- **Database query response time**: P95 < 300ms
- **Web query response time**: P95 < 5 seconds (optional feature)
- **Page load time**: First screen load < 2 seconds
- **System availability**: 99% uptime

#### 4.4.3 User Experience Evaluation
- **Task completion rate**: Proportion of users successfully completing search tasks > 90%
- **Error rate**: Proportion of failed user operations < 5%
- **Learning curve**: New users can master core features within 5 minutes

### 4.5 Ethics and Compliance

#### 4.5.1 Data Privacy
- User passwords encrypted (bcrypt + salt)
- User query history visible only to themselves
- No cross-user sharing of personal knowledge base data
- Comply with GDPR/CCPA data protection regulations (if applicable)

#### 4.5.2 Content Security
- Sensitive information filtering: filter content involving violence, pornography, etc.
- Source traceability: retain original source information for all data
- Copyright respect: only store news summaries, provide original links instead of full-text reproduction

#### 4.5.3 Algorithm Fairness
- Search results should not discriminate based on user identity
- Diversity assurance: avoid search results being overly concentrated on a single source or viewpoint
- Transparency: explain AI system's working principles to users

#### 4.5.4 Web Crawler Compliance
- Comply with robots.txt protocol
- Control crawling frequency to avoid pressuring target websites
- Respect website terms of use

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **Response Time**:
  - Page load: < 2 seconds
  - List query: < 300ms (SQLite index optimization)
  - Full-text search: < 1 second (FTS5 full-text index)
  - Web query: < 5 seconds (optional feature)
- **Concurrency**:
  - Based on SQLite single-machine deployment, supports 10-20 concurrent users
  - Use SQLite WAL mode to improve read-write concurrency
  - Read operations can be concurrent, write operations serialized
- **Database Query Optimization**:
  - Add B-Tree indexes on user_id, category, created_at fields
  - Use FTS5 virtual table for full-text indexing
  - Query plan optimization, avoid full table scans
  - Response time < 500ms

### 5.2 Security Requirements
- **Authentication**:
  - Password strength requirement: at least 8 characters, including letters + numbers
  - Session timeout: auto-logout after 30 minutes of inactivity
  - Brute force protection: lock account for 15 minutes after 5 consecutive failures
- **Data transmission**: HTTPS encryption site-wide
- **SQL injection protection**: use parameterized queries
- **XSS protection**: escape user input
- **CSRF protection**: use CSRF Token

### 5.3 Availability Requirements
- **System availability**: 99% uptime (< 7.2 hours downtime per month)
- **Fault tolerance**:
  - External API (like Baidu Search) failures degrade gracefully without affecting core functions
  - Display friendly message when database connection fails
- **Backup and recovery**:
  - Database daily auto-backup
  - Support one-click restore to any point in last 7 days

### 5.4 Maintainability Requirements
- **Code standards**: follow PEP8 (Python) or respective language code standards
- **Logging**:
  - Record all user operations (login, query, delete, etc.)
  - Record system errors and exceptions
  - Log retention period: 90 days
- **Monitoring and alerts**:
  - System performance monitoring (CPU, memory, disk)
  - API availability monitoring
  - Abnormal traffic alerts

### 5.5 Compatibility Requirements
- **Browser compatibility**:
  - Chrome 90+
  - Firefox 88+
  - Safari 14+
  - Edge 90+
- **Mobile**: responsive design, supports mobile browser access
- **Operating system**: cross-platform deployment (Linux, Windows)

### 5.6 Scalability Requirements
- **Vertical scaling**:
  - SQLite single-file database, lightweight deployment
  - When data exceeds 50,000 items, recommend migrating to PostgreSQL
  - For semantic search needs, can integrate FAISS or vector database later
- **Feature expansion**:
  - Modular design, easy to add new features
  - Standard API interface, supports third-party integration (like n8n)
  - Reserved interface can upgrade to vector search
- **Backup and recovery**:
  - SQLite database file can be directly copied for backup
  - Support export to JSON/CSV format
  - Support scheduled auto-backup
  - One-click recovery function

---

## 6. Release Standards and Metrics

### 6.1 Release Standards (DoD - Definition of Done)

#### 6.1.1 Feature Completeness
- [ ] All P0 features developed and tested
- [ ] User authentication system working (registration, login, permission verification)
- [ ] Knowledge base management features complete (view, filter, delete, edit, upload)
- [ ] Semantic search feature available, search accuracy meets standards
- [ ] Web query feature triggers and returns results normally
- [ ] Data analysis reports generate and display normally

#### 6.1.2 Quality Standards
- [ ] Unit test coverage > 70%
- [ ] Integration test pass rate 100%
- [ ] No P0/P1 level bugs
- [ ] Performance tests meet standards (response time, concurrency)
- [ ] Security scan shows no high-risk vulnerabilities

#### 6.1.3 User Experience
- [ ] UI/UX review passed
- [ ] Completed usability testing with at least 5 target users
- [ ] User feedback satisfaction > 4 points (5-point scale)

#### 6.1.4 Documentation Completeness
- [ ] User manual
- [ ] API documentation (if applicable)
- [ ] Deployment documentation
- [ ] Operations manual

### 6.2 Metrics (KPI)

#### 6.2.1 Usage Metrics
- **Daily Active Users (DAU)**: target > 50 users (first month)
- **Monthly Active Users (MAU)**: target > 200 users (first month)
- **User retention rate**:
  - Next-day retention > 50%
  - 7-day retention > 30%
  - 30-day retention > 20%

#### 6.2.2 Feature Usage Metrics
- **Search usage rate**: average searches per active user per day > 5
- **Upload usage rate**: at least 30% of users have used upload feature
- **Analysis report view rate**: at least 40% of users have viewed data analysis reports

#### 6.2.3 Performance Metrics
- **System response time**:
  - List query: P95 < 300ms
  - Full-text search: P95 < 1 second
  - Overall page response: P95 < 2 seconds
- **System availability**: > 99%
- **Error rate**: < 0.5%
- **Database size**: single file < 1GB (10,000 documents)

#### 6.2.4 Satisfaction Metrics
- **NPS (Net Promoter Score)**: > 40
- **Feature satisfaction**: > 4 points (5-point scale)
- **User feedback response rate**: 100% (respond within 24 hours)

#### 6.2.5 Business Metrics
- **Knowledge base growth rate**: monthly new data > 1,000 items
- **Data quality**: proportion of user-deleted data < 5%
- **Query success rate**: proportion of user queries finding relevant results > 70%
- **Search accuracy**: proportion of relevant documents in returned results > 60%

---

## 7. Pending Items and Future Planning

### 7.1 Pending Items (Need Further Confirmation)

#### 7.1.1 User Authentication Approach
- **Pending**: Whether to support third-party login (GitHub, Google OAuth)
- **Pending**: Whether email verification is needed
- **Pending**: Password reset process (email reset vs admin reset)

#### 7.1.2 Data Permissions
- **Pending**: Whether to support multi-user shared knowledge base
- **Pending**: Whether role permission system is needed (admin, regular user)

#### 7.1.3 Web Query
- **Pending**: Besides Baidu Search, whether to integrate other search engines (Google, Bing)
- **Pending**: Whether web query results auto-save to database (user confirmation vs auto-save)

#### 7.1.4 Data Analysis
- **Pending**: Auto-generation frequency for analysis reports (daily, weekly)
- **Pending**: Whether to support custom analysis dimensions

### 7.2 Future Planning (V2.0 and Beyond)

#### 7.2.1 Social and Collaboration Features
- Knowledge base sharing (generate share links)
- Multi-user collaborative knowledge base (team version)
- User comments and annotations

#### 7.2.2 Intelligent Recommendations
- News recommendations based on user interests
- Related news recommendations ("You may be interested")
- Proactive alerts (keyword monitoring, push when new content available)

#### 7.2.3 Advanced Analysis
- Sentiment analysis (news emotional tendency)
- Entity recognition (people, places, organizations)
- Event timeline tracking (news event timelines)
- Viewpoint comparison analysis (viewpoint differences from different sources)

#### 7.2.4 Multimodal Support
- Image news recognition and search
- Video news subtitle extraction and search
- Voice input query

#### 7.2.5 Mobile Applications
- Develop standalone iOS/Android apps
- Support offline viewing
- Push notifications

#### 7.2.6 API Opening
- Provide RESTful API for third-party integration
- Webhook mechanism (notify when new data is stored)
- Browser plugin (one-click save webpage to knowledge base)

#### 7.2.7 Enhanced AI Capabilities
- Multi-turn conversational query (context understanding)
- Auto-generate news summaries
- Multi-document comparison and comprehensive analysis
- Knowledge base-based Q&A system

#### 7.2.8 Personalization
- Custom interface themes
- Custom search algorithm parameters
- Custom data sources (user adds RSS feeds)

---

## Appendix

### A. Recommended Tech Stack
- **Backend Framework**: Flask (Python)
- **Frontend Framework**: Vue.js + Element Plus
- **Database**: SQLite (relational data + document content storage + full-text search)
- **Full-Text Search**: SQLite FTS5 (full-text search extension)
- **Chinese Segmentation**: jieba (for Chinese keyword extraction and segmentation)
- **Authentication**: Flask-JWT-Extended
- **Search API**: Baidu Search API (optional)

### B. Key Technical Challenges
1. **SQLite Performance Optimization**:
   - Proper index design (user_id, category, created_at)
   - Use FTS5 virtual table for efficient full-text search
   - Optimize large text field storage and queries
   - Regularly execute VACUUM for database maintenance
   - Enable WAL mode for improved concurrency
2. **Chinese Full-Text Search Optimization**:
   - Use jieba for Chinese word segmentation
   - Build Chinese keyword inverted index
   - Support synonym and near-synonym expansion (optional)
   - Handle stop words (的, 了, 是, etc.)
3. **Search Relevance Ranking**:
   - BM25 algorithm for document relevance calculation
   - TF-IDF weight calculation
   - Hybrid ranking combining time factors
4. **Concurrency Handling**:
   - SQLite WAL mode supports read-write concurrency
   - Connection pool management to avoid resource exhaustion
   - Long query timeout control

### C. References
- [SQLite Official Documentation](https://www.sqlite.org/docs.html)
- [SQLite FTS5 Full-Text Search](https://www.sqlite.org/fts5.html)
- [jieba Chinese Segmentation](https://github.com/fxsjy/jieba)
- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Vue.js Official Documentation](https://vuejs.org/)

### D. Technical Architecture Diagram
```
┌─────────────────────────────────────┐
│          Frontend (Vue.js)           │
│  - Knowledge Base Management         │
│  - Full-Text Search                  │
│  - Data Analysis                     │
└────────────┬────────────────────────┘
             │ HTTP API
             ▼
┌─────────────────────────────────────┐
│       Backend (Flask)                │
│  - RESTful API                       │
│  - JWT Authentication                │
│  - Document Parsing                  │
│  - Chinese Segmentation (jieba)      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      SQLite Database (single file)   │
│  ┌─────────────────────────────┐    │
│  │  documents table            │    │
│  │  - User data                │    │
│  │  - Document title & content │    │
│  │  - Metadata (category/tags) │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  FTS5 virtual table (opt.)  │    │
│  │  - Full-text index          │    │
│  │  - Keyword matching         │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

---

**Document Version**: V1.0  
**Created**: 2025-10-01  
**Updated**: 2025-10-01  
**Owner**: AI Requirements Analyst  
**Review Status**: Pending Review

