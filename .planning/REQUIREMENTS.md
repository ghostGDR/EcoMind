# Requirements: Henry - AI 电商专家对话系统

**Defined:** 2026-04-22
**Core Value:** 用户能够与基于自己知识库的 AI 专家进行自然对话，获得准确的电商建议，并通过反馈让这个专家持续进化。

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### 对话功能 (Conversation)

- [ ] **CHAT-01**: 用户可以在网页界面输入问题并看到 Henry 的回答
- [ ] **CHAT-02**: 用户可以进行多轮对话，Henry 记住之前的对话内容
- [ ] **CHAT-03**: 用户可以查看所有历史对话记录
- [ ] **CHAT-04**: 用户可以在对话中直接教 Henry 新知识（如"记住：TikTok 广告投放最佳时间是晚上 8-10 点"）
- [ ] **CHAT-05**: 系统自动管理对话上下文窗口，长对话不会导致 API 错误
- [ ] **CHAT-06**: Henry 的回答风格符合电商专家的专业语气

### 检索与搜索 (Retrieval & Search)

- [ ] **SEARCH-01**: Henry 基于语义理解回答问题，不只是关键词匹配
- [ ] **SEARCH-02**: Henry 的每个回答都引用具体的来源文章和段落
- [ ] **SEARCH-03**: 系统使用混合检索（语义 + 关键词），提升准确度
- [ ] **SEARCH-04**: 系统使用智能分块策略，保持语义完整性
- [ ] **SEARCH-05**: 用户可以搜索文章内容，找到相关文档

### 文档管理 (Document Management)

- [ ] **DOC-01**: 用户可以浏览所有文章列表
- [ ] **DOC-02**: 用户可以按主题分类查看文章（TikTok、AI、财务、收款等）
- [ ] **DOC-03**: 用户可以读取完整文章内容，Markdown 正确渲染
- [ ] **DOC-04**: 用户可以上传新的 Markdown 文章到知识库
- [ ] **DOC-05**: 系统支持读取和搜索 Excel 文件内容
- [ ] **DOC-06**: 系统实时监控 `/Users/a1234/wiki/raw/articles` 目录变化，自动更新索引
- [ ] **DOC-07**: 用户可以编辑现有文章内容

### 学习与优化 (Learning & Optimization)

- [ ] **LEARN-01**: 用户可以对 Henry 的回答写详细反馈评价
- [ ] **LEARN-02**: 系统收集反馈数据，用于优化 Henry 的回答质量
- [ ] **LEARN-03**: 系统支持检索文章中的图片和图表内容

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### 高级功能

- **ADV-01**: 移动端 App 支持
- **ADV-02**: 语音对话功能
- **ADV-03**: 自动生成文章大纲建议
- **ADV-04**: 多用户协作功能
- **ADV-05**: 与外部系统集成（CRM、电商平台等）

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| 自动生成长文章 | AI 生成的长文容易偏离事实，需大量人工校验；提供大纲建议更实用 |
| 实时语音对话 | 增加复杂度（语音识别、TTS），文字对话已足够，v1 专注核心价值 |
| 多用户系统 | 权限管理、冲突解决复杂，v1 单用户已足够验证核心价值 |
| 完全自动化索引 | 自动索引可能误解文档结构，产生噪音；半自动更可控 |
| 无限对话历史 | 检索性能下降，上下文窗口爆炸；保留最近 N 条，提供归档功能 |
| 与外部系统集成 | 每个集成都是独立项目，分散核心价值；专注对话和知识管理 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| (To be filled during roadmap creation) | | |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 20 ⚠️

---
*Requirements defined: 2026-04-22*
*Last updated: 2026-04-22 after initial definition*
