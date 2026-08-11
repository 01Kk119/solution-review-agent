---
type: agent-risk-index-routing
status: active
updated: 2026-07-29
---

# 开发风险知识索引层

本目录是方案评审 Agent 的默认知识入口。这里的文档只保留判断“现有能力是否覆盖、是否可能需要新增软件或算法功能”所需的边界、触发条件和证据路径。

## 读取规则

1. 领域 Agent 默认只读本目录中与自己角色对应的索引，不直接展开源文件。
2. 软件能力先读 `software_core_development_risk_index.md` 和 `software_5_2_2_risk_index.md`。
3. 只有 5.2.2 缺少证据、明确不支持或适用条件不满足时，才读 `software_5_3_2_risk_index.md`。
4. 出现高风险、索引内无结论、证据冲突或唯一跨专业问题时，才按文末 `source_files` 回查源文件中的相关片段。
5. 源文件仍是最终权威依据；索引只用于缩小检索范围，不能扩大源文件能力。
6. “未给参数”不等于“无风险”。先按潜在影响给高/中/低等级，再降低置信度并登记待确认条件。

## 索引文件

| 角色 | 默认索引 |
|---|---|
| 取放 TPM | `pick_place_development_risk_index.md` |
| 导航 TPM | `navigation_development_risk_index.md` |
| 调度 TPM | `dispatch_development_risk_index.md` |
| 软件 TPM | `software_core_development_risk_index.md`、`software_5_2_2_risk_index.md` |
| 明眸 TPM | `brighteyes_development_risk_index.md` |
| 版本适配 Agent | 软件通用、5.2.2；有缺口后再读 5.3.2 |
| 人时估算 Agent | `effort_estimation_risk_index.md` |

