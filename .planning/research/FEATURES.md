# Feature Research

**Domain:** AI 对话系统和知识库管理 (AI Dialogue System & Knowledge Base Management)
**Researched:** 2026-04-22
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| 对话界面 (Chat Interface) | 核心交互方式，用户期望能自然对话 | LOW | 文本输入框、消息列表、实时响应 |
| 语义搜索 (Semantic Search) | AI 系统标配，关键词搜索已过时 | MEDIUM | 需要 embedding 模型和向量存储 |
| 对话历史 (Conversation History) | 用户期望系统"记住"上下文 | LOW | 持久化存储，按时间排序 |
| 文档浏览 (Document Browsing) | 知识库管理的基础功能 | LOW | 列表视图、分类、搜索 |
| 来源引用 (Source Citation) | AI 回答必须可验证，避免幻觉 | MEDIUM | 追踪检索到的文档片段，显示来源链接 |
| 多轮对话 (Multi-turn Conversation) | 对话系统基本能力 | MEDIUM | 需要 conversation memory 管理上下文 |
| 文档上传 (Document Upload) | 用户需要添加新知识 | LOW | 文件上传、格式验证、存储 |
| Markdown 支持 | 技术文档标准格式 | LOW | 渲染 Markdown，支持代码块、表格等 |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| 用户反馈学习 (Feedback Learning) | 让 AI 持续优化，个性化体验 | HIGH | 需要反馈收集、分析、模型微调机制 |
| 对话中教学 (In-conversation Teaching) | 无缝补充知识，无需切换界面 | MEDIUM | 识别教学意图，自动提取并存储新知识 |
| 智能分块 (Smart Chunking) | 提升检索准确度 | MEDIUM | 多种分块策略（recursive, semantic, paragraph） |
| 混合检索 (Hybrid Retrieval) | 结合语义和关键词，更鲁棒 | MEDIUM | BM25 + 向量搜索 + 重排序 (reranking) |
| 实时文件监控 (Real-time File Watching) | 自动同步外部知识库变化 | MEDIUM | 文件系统监控，增量索引更新 |
| 主题分类 (Topic Classification) | 快速定位相关文档 | LOW | 基于文档元数据或内容自动分类 |
| Excel 文件支持 | 处理结构化数据（财务表格等） | MEDIUM | 解析 Excel，转换为可检索格式 |
| 上下文窗口管理 (Context Window Management) | 优化长对话性能 | MEDIUM | 智能压缩历史，保留关键信息 |
| 多模态检索 (Multi-modal Retrieval) | 支持图片、图表等非文本内容 | HIGH | 需要图像 captioning 或 VLM 模型 |
| 个性化回答风格 (Personalized Response Style) | 匹配用户的专业领域和语气 | MEDIUM | 基于用户反馈调整生成参数 |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| 自动生成长文章 (Auto-generate Long Articles) | 用户想"一键生成内容" | AI 生成的长文容易偏离事实，需大量人工校验 | 提供大纲建议，用户自己写作 |
| 实时语音对话 (Real-time Voice Chat) | 看起来很酷 | 增加复杂度（语音识别、TTS），文字对话已足够 | 专注文字对话，未来再考虑 |
| 多用户协作 (Multi-user Collaboration) | 团队使用场景 | 权限管理、冲突解决复杂，v1 单用户已足够 | 先验证单用户价值，再扩展 |
| 与外部系统集成 (External System Integration) | 连接 CRM、电商平台等 | 每个集成都是独立项目，分散核心价值 | 专注对话和知识管理，导出数据供外部使用 |
| 完全自动化索引 (Fully Automated Indexing) | 用户不想手动管理 | 自动索引可能误解文档结构，产生噪音 | 半自动：系统建议，用户确认 |
| 无限对话历史 (Unlimited Conversation History) | 用户想保留所有记录 | 检索性能下降，上下文窗口爆炸 | 保留最近 N 条，提供归档功能 |

## Feature Dependencies

```
[语义搜索 (Semantic Search)]
    └──requires──> [文档分块 (Document Chunking)]
                       └──requires──> [文档解析 (Document Parsing)]

[多轮对话 (Multi-turn Conversation)]
    └──requires──> [对话历史 (Conversation History)]
                       └──requires──> [Conversation Memory]

[来源引用 (Source Citation)]
    └──requires──> [语义搜索 (Semantic Search)]

[用户反馈学习 (Feedback Learning)]
    └──requires──> [对话历史 (Conversation History)]
    └──requires──> [反馈收集 (Feedback Collection)]

[混合检索 (Hybrid Retrieval)] ──enhances──> [语义搜索 (Semantic Search)]

[实时文件监控 (Real-time File Watching)] ──enhances──> [文档上传 (Document Upload)]

[智能分块 (Smart Chunking)] ──enhances──> [语义搜索 (Semantic Search)]

[对话中教学 (In-conversation Teaching)] ──conflicts──> [完全自动化索引 (Fully Automated Indexing)]
```

### Dependency Notes

- **语义搜索 requires 文档分块:** 必须先将文档切分成可检索的片段，才能进行向量搜索
- **多轮对话 requires 对话历史:** 需要持久化存储和检索历史消息，才能维持上下文
- **来源引用 requires 语义搜索:** 引用来源依赖于检索系统返回的文档片段
- **混合检索 enhances 语义搜索:** 结合 BM25 和向量搜索，提升检索鲁棒性
- **对话中教学 conflicts with 完全自动化索引:** 教学功能需要用户主动确认新知识，与全自动索引的理念冲突

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **对话界面** — 核心价值：用户与 AI 专家对话
- [x] **语义搜索** — 核心价值：基于知识库的准确回答
- [x] **对话历史** — 基础体验：连续多轮对话
- [x] **来源引用** — 信任建立：回答可验证
- [x] **文档浏览** — 知识管理：查看和搜索文档
- [x] **文档上传** — 知识扩展：添加新文档
- [x] **Markdown 支持** — 技术文档标准
- [x] **主题分类** — 快速定位：按主题浏览文档

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **用户反馈学习** — 触发条件：用户开始频繁使用，需要个性化优化
- [ ] **对话中教学** — 触发条件：用户反馈"AI 不知道某些知识"
- [ ] **混合检索** — 触发条件：语义搜索准确率不足
- [ ] **智能分块** — 触发条件：检索结果质量需要优化
- [ ] **实时文件监控** — 触发条件：用户频繁手动上传更新的文档
- [ ] **Excel 文件支持** — 触发条件：用户有结构化数据需求
- [ ] **上下文窗口管理** — 触发条件：长对话导致性能问题

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **多模态检索** — 延迟原因：需要图像处理能力，复杂度高
- [ ] **个性化回答风格** — 延迟原因：需要大量用户数据训练
- [ ] **多用户协作** — 延迟原因：单用户价值未验证
- [ ] **语音对话** — 延迟原因：文字对话已足够，语音是锦上添花
- [ ] **外部系统集成** — 延迟原因：核心价值未稳定

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| 对话界面 | HIGH | LOW | P1 |
| 语义搜索 | HIGH | MEDIUM | P1 |
| 对话历史 | HIGH | LOW | P1 |
| 来源引用 | HIGH | MEDIUM | P1 |
| 文档浏览 | HIGH | LOW | P1 |
| 文档上传 | HIGH | LOW | P1 |
| Markdown 支持 | HIGH | LOW | P1 |
| 主题分类 | MEDIUM | LOW | P1 |
| 用户反馈学习 | HIGH | HIGH | P2 |
| 对话中教学 | HIGH | MEDIUM | P2 |
| 混合检索 | MEDIUM | MEDIUM | P2 |
| 智能分块 | MEDIUM | MEDIUM | P2 |
| 实时文件监控 | MEDIUM | MEDIUM | P2 |
| Excel 文件支持 | MEDIUM | MEDIUM | P2 |
| 上下文窗口管理 | MEDIUM | MEDIUM | P2 |
| 多模态检索 | LOW | HIGH | P3 |
| 个性化回答风格 | LOW | MEDIUM | P3 |
| 多用户协作 | LOW | HIGH | P3 |
| 语音对话 | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (MVP)
- P2: Should have, add when possible (v1.x)
- P3: Nice to have, future consideration (v2+)

## Competitor Feature Analysis

| Feature | Notion AI | Obsidian + AI Plugin | ChatGPT + Custom GPT | Our Approach |
|---------|-----------|----------------------|----------------------|--------------|
| 对话界面 | ✅ 集成在文档中 | ✅ 插件提供 | ✅ 原生支持 | ✅ 独立对话界面 |
| 语义搜索 | ✅ Enterprise Search | ⚠️ 依赖插件 | ✅ 基于上传文件 | ✅ 本地向量搜索 |
| 对话历史 | ⚠️ 有限支持 | ❌ 无 | ✅ 完整历史 | ✅ 持久化存储 |
| 来源引用 | ⚠️ 部分支持 | ❌ 无 | ⚠️ 有时提供 | ✅ 强制引用来源 |
| 文档管理 | ✅ 强大的知识库 | ✅ 本地文件管理 | ❌ 仅上传文件 | ✅ 本地文件 + 分类 |
| 用户反馈 | ❌ 无学习机制 | ❌ 无 | ⚠️ 点赞/点踩 | ✅ 详细反馈 + 学习 |
| 对话中教学 | ❌ 无 | ❌ 无 | ❌ 无 | ✅ 核心差异化功能 |
| 本地运行 | ❌ 云服务 | ✅ 完全本地 | ❌ 云服务 | ✅ 本地运行 |
| 数据隐私 | ⚠️ 云端存储 | ✅ 完全私有 | ⚠️ 云端存储 | ✅ 完全私有 |
| 实时文件监控 | ❌ 无 | ⚠️ 手动刷新 | ❌ 无 | ✅ 自动同步 |

**Our Competitive Advantages:**
1. **对话中教学** — 独有功能，无缝补充知识
2. **强制来源引用** — 确保回答可验证，建立信任
3. **本地运行 + 完全隐私** — 商业知识敏感，数据不出本地
4. **实时文件监控** — 自动同步外部知识库变化
5. **详细反馈学习** — 持续优化个性化体验

## Sources

### High Confidence (Context7 + Official Docs)
- **RAG System Features:** Context7 `/get-convex/rag` — Semantic search, chunking, filtering, reranking
- **RAG Techniques:** Context7 `/nirdiamant/rag_techniques` — Ensemble retrieval, fusion retrieval, multi-faceted filtering
- **Conversation Memory:** Context7 `/websites/langchain` — ConversationBufferMemory, ConversationalRetrievalChain
- **Groq RAG Features:** Context7 `/mithun50/groq-rag` — RAG initialization, document management, query API

### Medium Confidence (Product Research)
- **Notion AI:** https://notion.so — Knowledge base, AI search, agents (2026-04-22)
- **Obsidian:** https://obsidian.md — Personal knowledge management, linking, graph view (2026-04-22)
- **GitHub Copilot:** https://github.com/features/copilot — AI assistance, code completion, chat (2026-04-22)

### Domain Knowledge (Training Data)
- Personal knowledge base systems (Roam Research, Logseq, etc.)
- RAG best practices (chunking strategies, retrieval optimization)
- Conversational AI patterns (memory management, context handling)

---
*Feature research for: AI 对话系统和知识库管理*
*Researched: 2026-04-22*
