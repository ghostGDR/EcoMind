# Roadmap: Henry - AI 电商专家对话系统

**Milestone:** v1.0
**Granularity:** fine (8-12 phases, 5-10 plans each)
**Created:** 2026-04-22
**Status:** Planning

## Phases

- [x] **Phase 1: Data Layer Foundation** - 建立向量存储和数据库基础设施
- [x] **Phase 2: Knowledge Base Indexing** - 实现文档解析、分块和向量化索引
- [ ] **Phase 3: Semantic Search Implementation** - 构建混合检索引擎（语义+关键词）
- [ ] **Phase 4: RAG Engine Core** - 集成检索与 LLM 生成带来源引用的答案
- [ ] **Phase 5: Conversation Management** - 实现多轮对话和上下文窗口管理
- [ ] **Phase 6: Backend API Layer** - 构建 FastAPI 接口层（REST + WebSocket）
- [ ] **Phase 7: Frontend UI - Chat Interface** - 构建对话界面和历史记录展示
- [ ] **Phase 8: Frontend UI - Document Management** - 构建文档浏览、上传和编辑界面
- [ ] **Phase 9: Real-time Knowledge Base Updates** - 实现文件系统监控和自动索引更新
- [ ] **Phase 10: User Feedback & Learning** - 构建反馈收集和学习优化系统
- [ ] **Phase 11: Performance Optimization** - 优化响应时间和系统性能

## Phase Details

### Phase 1: Data Layer Foundation
**Goal**: 建立持久化存储基础设施，支持向量搜索和对话历史管理
**Depends on**: Nothing (first phase)
**Requirements**: (Infrastructure - enables all other requirements)
**Success Criteria** (what must be TRUE):
  1. Qdrant 向量数据库在本地运行并可以存储/查询向量
  2. SQLite 数据库可以持久化保存对话历史记录
  3. 文档存储接口可以读取 `/Users/a1234/wiki/raw/articles` 目录中的文件
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Initialize Qdrant vector database with LlamaIndex integration
- [x] 01-02-PLAN.md — Initialize SQLite database for conversation history
- [x] 01-03-PLAN.md — Implement document storage interface for file system access

### Phase 2: Knowledge Base Indexing
**Goal**: 用户的 22 篇文章被正确解析、分块并索引到向量数据库
**Depends on**: Phase 1
**Requirements**: DOC-04, DOC-05, DOC-03
**Success Criteria** (what must be TRUE):
  1. 系统可以解析 Markdown 文件并保持格式完整性
  2. 系统可以读取 Excel 文件内容并提取结构化数据
  3. 文档被智能分块（保持语义完整性，支持中英文混合）
  4. 所有 22 篇文章的向量嵌入已存储在 Qdrant 中
**Plans**: 1 plan

Plans:
- [x] 02-01-PLAN.md — Build document ingestion pipeline and index all 21 wiki articles

### Phase 3: Semantic Search Implementation
**Goal**: 用户可以通过语义理解搜索文档，获得准确的相关内容
**Depends on**: Phase 2
**Requirements**: SEARCH-01, SEARCH-03, SEARCH-04, SEARCH-05, DOC-01, DOC-02
**Success Criteria** (what must be TRUE):
  1. 用户输入中文问题可以找到语义相关的文档（不只是关键词匹配）
  2. 混合检索（语义+关键词）可以处理专业术语和精确匹配需求
  3. 检索结果包含相关性评分，低质量结果被过滤
  4. 用户可以浏览文章列表并按主题分类查看
  5. 用户可以搜索文章内容并找到相关文档
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — 实现语义搜索引擎，支持中文查询和混合检索
- [ ] 03-02-PLAN.md — 实现文档浏览和主题分类功能

### Phase 4: RAG Engine Core
**Goal**: 系统可以基于检索到的文档生成准确的答案，并引用具体来源
**Depends on**: Phase 3
**Requirements**: SEARCH-02, CHAT-01, CHAT-06
**Success Criteria** (what must be TRUE):
  1. 用户提问后，系统返回基于知识库的答案（不是通用知识）
  2. 每个答案都引用具体的来源文章和段落
  3. Henry 的回答风格符合电商专家的专业语气
  4. 当知识库中没有相关信息时，系统明确告知用户
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — Configure LLM integration and Henry's e-commerce expert persona
- [ ] 04-02-PLAN.md — Build RAG query engine integrating search with LLM generation
- [ ] 04-03-PLAN.md — Add citation formatting to reference source articles

### Phase 5: Conversation Management
**Goal**: 用户可以进行多轮对话，Henry 记住上下文并保持对话连贯性
**Depends on**: Phase 4
**Requirements**: CHAT-02, CHAT-03, CHAT-05
**Success Criteria** (what must be TRUE):
  1. 用户可以进行多轮对话，Henry 理解之前的对话内容
  2. 对话历史持久化保存，刷新页面后仍可查看
  3. 长对话不会导致 API 错误（上下文窗口自动管理）
  4. 用户可以查看所有历史对话记录
**Plans**: TBD

### Phase 6: Backend API Layer
**Goal**: 前端可以通过稳定的 API 接口访问 RAG 引擎和对话管理功能
**Depends on**: Phase 5
**Requirements**: (Infrastructure - enables frontend integration)
**Success Criteria** (what must be TRUE):
  1. FastAPI 服务在本地运行并提供 REST 接口
  2. WebSocket/SSE 接口支持流式响应（实时显示 Henry 的回答）
  3. API 请求验证和错误处理正常工作
  4. API 文档自动生成并可访问
**Plans**: TBD

### Phase 7: Frontend UI - Chat Interface
**Goal**: 用户可以在网页界面与 Henry 自然对话并查看历史记录
**Depends on**: Phase 6
**Requirements**: CHAT-01, CHAT-03, SEARCH-02
**Success Criteria** (what must be TRUE):
  1. 用户可以在网页界面输入问题并看到 Henry 的回答
  2. 回答以流式方式实时显示（不是等待全部生成完成）
  3. 对话历史在界面中正确展示（多轮对话上下文清晰）
  4. 来源引用在界面中可点击查看原文
**Plans**: TBD
**UI hint**: yes

### Phase 8: Frontend UI - Document Management
**Goal**: 用户可以浏览、上传和编辑知识库文档
**Depends on**: Phase 6
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-07
**Success Criteria** (what must be TRUE):
  1. 用户可以浏览所有文章列表并按主题分类查看
  2. 用户可以读取完整文章内容，Markdown 正确渲染
  3. 用户可以上传新的 Markdown 文章到知识库
  4. 用户可以编辑现有文章内容
  5. 上传/编辑后，文档自动重新索引
**Plans**: TBD
**UI hint**: yes

### Phase 9: Real-time Knowledge Base Updates
**Goal**: 外部文件变化自动同步到系统，无需手动触发索引
**Depends on**: Phase 8
**Requirements**: DOC-06
**Success Criteria** (what must be TRUE):
  1. 系统监控 `/Users/a1234/wiki/raw/articles` 目录的文件变化
  2. 新增文件自动索引到向量数据库
  3. 修改文件自动更新索引
  4. 删除文件自动从索引中移除
**Plans**: TBD

### Phase 10: User Feedback & Learning
**Goal**: 用户可以对 Henry 的回答提供反馈，系统收集数据用于优化
**Depends on**: Phase 7
**Requirements**: CHAT-04, LEARN-01, LEARN-02
**Success Criteria** (what must be TRUE):
  1. 用户可以对每个回答写详细反馈评价（点赞/点踩 + 文字评论）
  2. 用户可以在对话中直接教 Henry 新知识（如"记住：TikTok 广告投放最佳时间是晚上 8-10 点"）
  3. 反馈数据持久化保存并关联到具体对话和文档
  4. 系统提供反馈数据分析界面（识别高频问题和改进机会）
**Plans**: TBD
**UI hint**: yes

### Phase 11: Performance Optimization
**Goal**: 系统响应时间满足 <2 秒要求，资源使用高效
**Depends on**: Phase 10
**Requirements**: LEARN-03
**Success Criteria** (what must be TRUE):
  1. 搜索响应时间 < 2 秒（90% 的查询）
  2. 对话生成响应时间 < 3 秒（首字节）
  3. 系统支持检索文章中的图片和图表内容
  4. 批量索引性能优化（新增 10 篇文章 < 30 秒）
  5. 性能监控仪表板显示关键指标
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Layer Foundation | 0/? | Not started | - |
| 2. Knowledge Base Indexing | 0/? | Not started | - |
| 3. Semantic Search Implementation | 0/? | Not started | - |
| 4. RAG Engine Core | 0/? | Not started | - |
| 5. Conversation Management | 0/? | Not started | - |
| 6. Backend API Layer | 0/? | Not started | - |
| 7. Frontend UI - Chat Interface | 0/? | Not started | - |
| 8. Frontend UI - Document Management | 0/? | Not started | - |
| 9. Real-time Knowledge Base Updates | 0/? | Not started | - |
| 10. User Feedback & Learning | 0/? | Not started | - |
| 11. Performance Optimization | 0/? | Not started | - |

---
*Last updated: 2026-04-22*
