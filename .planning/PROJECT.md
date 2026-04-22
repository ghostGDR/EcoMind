# Henry - AI 电商专家对话系统

## What This Is

一个基于个人知识库的 AI 对话系统，让用户与虚拟电商专家 "Henry" 对话。Henry 基于用户的 22 篇跨境电商文章（涵盖 TikTok、AI 工具、财务、收款、流量、广告投放等主题）回答问题，并通过用户反馈和新知识持续学习优化。系统提供可视化网页界面来管理文档、查看对话历史、评价回答质量。

## Core Value

用户能够与基于自己知识库的 AI 专家进行自然对话，获得准确的电商建议，并通过反馈让这个专家持续进化。

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 用户可以在网页界面与 Henry 对话
- [ ] Henry 基于知识库文章回答问题（语义理解，不只是关键词匹配）
- [ ] 对话历史持久化保存，可以连续多轮对话
- [ ] 用户可以查看所有历史对话记录
- [ ] 用户可以对 Henry 的回答写详细反馈评价
- [ ] 用户可以在对话中直接教 Henry 新知识，系统自动记录
- [ ] 用户可以浏览文章列表，按主题分类（TikTok、AI、财务等）
- [ ] 用户可以读取完整文章内容（Markdown 和 Excel）
- [ ] 用户可以搜索文章内容（智能语义搜索）
- [ ] 用户可以上传新的 Markdown 文章到知识库
- [ ] 用户可以编辑现有文章内容
- [ ] 系统实时读取 `/Users/a1234/wiki/raw/articles` 目录变化
- [ ] Henry 的回答会引用具体的文章来源

### Out of Scope

- 多用户系统 — v1 只服务单个用户（你自己）
- 移动端 App — 先做好网页版
- 语音对话 — 文字对话足够
- 自动生成新文章 — Henry 只回答问题，不主动创作长文
- 与外部系统集成（CRM、电商平台等）— 专注对话和知识管理

## Context

**用户背景：**
- 拥有 22 篇跨境电商领域的知识文章
- 文章涵盖：TikTok 运营、AI 工具应用、财务规划、收款风控、流量获取、广告投放等
- 文章格式：主要是 Markdown，包含一个 Excel 文件
- 文章会持续更新和增加

**使用场景：**
- 用户在做电商决策时，向 Henry 咨询专业建议
- Henry 基于用户自己的知识库回答，确保答案符合用户的方法论
- 用户通过反馈纠正 Henry 的理解偏差
- 用户通过对话或文档管理补充新知识

**技术环境：**
- 本地运行（数据隐私）
- 需要访问本地文件系统读取文章
- 需要 LLM API（Claude/OpenAI）进行对话

## Constraints

- **数据隐私**: 所有数据本地存储，不上传到第三方服务 — 用户的商业知识敏感
- **文章路径**: 固定读取 `/Users/a1234/wiki/raw/articles` — 用户现有文章位置
- **性能**: 搜索响应时间 < 2 秒 — 对话体验流畅
- **兼容性**: 支持 Markdown 和 Excel 文件格式 — 现有文章格式

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 本地运行而非云服务 | 保护商业知识隐私，用户完全控制数据 | — Pending |
| 单用户系统 | 简化开发，专注核心功能 | — Pending |
| 语义搜索而非关键词 | 理解问题意图，提供更准确的答案 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-22 after initialization*
