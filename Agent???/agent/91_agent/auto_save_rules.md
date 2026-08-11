---
type: agent-guide
status: active
created: 2026-07-28
updated: 2026-07-29
---

# 评审结果自动保存

> 导航：[[home|知识库首页]] · [[knowledge_base_map]] · [[review_index]] · [[solution_review_template]]

## 目标

每次 Agent 完成方案评审后，自动在本知识库创建一份可由 Obsidian 直接查看的 Markdown 报告。

## 保存位置

```text
review_outputs/<project_key>/
├─ project_output_index.md
├─ step1_requirements/
├─ step2_domain_review/
├─ step3_evidence_critique/
├─ step4_delivery_decisions/
└─ final/
```

## 阶段与文件

| 目录 | 内容 | 推荐文件名 |
|---|---|---|
| `step1_requirements` | 需求模型、证据索引、缺失信息、结构化抽取和引用附件 | `<project_key>_requirements_model_<YYYYMMDD>_v<NNN>.md` |
| `step2_domain_review` | 各领域评审、跨专业问答和领域汇总 | `<project_key>_domain_review_<YYYYMMDD>_v<NNN>.md` |
| `step3_evidence_critique` | 无依据结论、错引、冲突和过度推断检查 | `<project_key>_evidence_critique_<YYYYMMDD>_v<NNN>.md` |
| `step4_delivery_decisions` | 版本、配置、非标、开发量、人时和现场适配决策 | `<project_key>_delivery_decisions_<YYYYMMDD>_v<NNN>.md` |
| `final` | 面向用户的最终方案评审报告 | `<project_key>_final_review_<YYYYMMDD>_v<NNN>.md` |

中间产物不能替代最终报告。

## 文件命名

所有阶段产物必须包含生成日期和三位版本号：

`<project_key>_<content_label>_<YYYYMMDD>_v<NNN>.md`

示例：

`vn26068_final_review_20260729_v002.md`

版本号规则：

- 首次评审使用 `v001`。
- “重新评审并保留历史”时，保留旧运行记录，将当前 Obsidian 结果移入对应阶段的 `history/`，新结果版本号递增，例如 `v001 → v002`。
- “清空全部结果并重新评审”时，删除该项目全部历史评审结果和运行记录，新结果从 `v001` 重新开始。
- 同一次运行的 Step1–Step4 和 Final 必须使用相同日期及版本号。

重新评审的两种模式都不得删除项目、初始上传资料或 Agent 知识库。

## 保存步骤

1. 创建项目目录及 Step1 至 Step4、Final 五个阶段目录。
2. 每个阶段完成后，立即把结果保存到对应 Step 目录。
3. 最终汇总前检查 Step1 至 Step4 是否完成；缺失阶段必须在最终报告中说明。
4. 若选择保留历史，将上一版本阶段产物移入相应目录的 `history/<timestamp>/`。
5. 将新的最终 Markdown 写入 `final/<project_key>_final_review_<YYYYMMDD>_v<NNN>.md`。
6. 更新项目根目录的 `project_output_index.md`，把“唯一最终结果”链接指向新报告。
7. 更新知识库总 `review_index.md`。
8. 向用户返回最终报告完整路径，并明确说明中间产物所在阶段。

## 最低质量要求

- 必须记录原始方案或输入材料。
- 必须给出总体结论。
- 每个高风险问题必须提供依据或标注依据不足。
- 必须列出待确认事项。
- 必须说明 Agent 推断与评审局限。
- 默认状态必须是 `待人工复核`。

## 禁止事项

- 禁止在“保留历史”模式下覆盖或删除历史报告。
- 禁止把 `requirements_model.md`、`domain_review.md`、`evidence_critique.md` 或 `delivery_decisions.md` 称为最终结果。
- 禁止把 Agent 推断伪装成原始事实。
- 禁止把未经核验的内容写成规范要求。
- 禁止把密钥、密码、Token 或敏感个人信息写入报告。
- 禁止系统生成包含空格、逗号、括号或非 ASCII 字符的文件夹名和文件名。
