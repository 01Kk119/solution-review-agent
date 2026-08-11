---
type: agent-guide
status: active
created: 2026-07-28
updated: 2026-07-28
---

# 知识库地图

> 导航：[[home|知识库首页]] · [[AGENTS|Agent 协作规则]]

## 目录职责

| 目录 | 用途 | Agent 默认操作 |
|---|---|---|
| `agent/00_inbox/` | 待整理、待确认内容 | 可以新建 |
| `agent/01_projects/` | 项目索引与项目说明 | 读取；新建前确认项目归属 |
| `agent/03_knowledge/` | 可复用知识与评审依据 | 读取；新增内容需标明来源 |
| `agent/90_templates/` | 标准模板 | 读取；未经授权不修改 |
| `agent/91_agent/` | Agent 协作说明 | 读取；未经授权不修改 |
| `review_outputs/项目名称/step1_requirements/` | 需求模型与证据准备 | 可以按阶段新建 |
| `review_outputs/项目名称/step2_domain_review/` | 专业领域风险评审 | 可以按阶段新建 |
| `review_outputs/项目名称/step3_evidence_critique/` | 证据充分性与冲突检查 | 可以按阶段新建 |
| `review_outputs/项目名称/step4_delivery_decisions/` | 交付、版本与非标决策 | 可以按阶段新建 |
| `review_outputs/项目名称/final/` | 唯一最终评审报告 | 可以按规则新建 |

## 导航层级

1. 顶层首页：[[home|知识库首页]]
2. 协作导航：本页与 [[AGENTS|Agent 协作规则]]
3. 分区索引：[[project_index]]、[[knowledge_index]]、[[review_index]]
4. 具体内容：项目笔记、知识笔记和评审报告

## 关键入口

- 知识库首页：[[home]]
- Agent 权威规则：[[AGENTS|Agent 协作规则]]
- 项目入口：[[project_index]]
- 知识入口：[[knowledge_index]]
- 评审结果入口：[[review_index]]
- 待整理入口：[[inbox_index]]
- 评审模板：[[solution_review_template]]
- 自动保存说明：[[auto_save_rules]]
- TPM 知识路由：[[tpm_knowledge_routing]]

## 建议检索顺序

1. 确定评审对象和项目范围。
2. 读取项目目录中的需求、方案和历史决策。
3. 从 `agent/03_knowledge/` 查找适用的规范、方法和案例。
4. 按 Step1 至 Step4 依次保存阶段结果。
5. 汇总生成 `final/<project_key>_final_review.md`。
6. 检查历史评审结果，避免重复问题并识别版本变化。
7. 将新报告加入 [[review_index#待人工复核|待人工复核]]，并更新项目的 `project_output_index.md`。
