---
type: agent-guide
status: active
updated: 2026-07-29
---

# TPM Knowledge Routing

本文件记录每个 TPM Agent 的知识文件白名单。项目事实始终来自当前项目资料；知识文件只用于能力边界对照、风险检查和提出待确认问题。

| Agent | Knowledge files |
|---|---|
| Navigation TPM | `capability_specs/navigation_capability_spec.md`; `shared_references/probabilistic_robotics_ch02_recursive_state_estimation.md`; `shared_references/probabilistic_robotics_ch03_gaussian_filters.md` |
| Dispatch TPM | `capability_specs/dispatch_capability_spec.md` |
| Software/RCS/Interface/HMI TPM | `shared_references/product_release_notes_5_2_2_20250930.md`; `shared_references/product_release_notes_5_3_2_20260430.md` |
| Hardware/Safety/Site TPM | `capability_specs/vehicle_body_capability_spec.md`; `capability_specs/load_carrier_capability_spec.md`; `capability_specs/pick_and_place_capability_spec.md` |
| Brighteyes TPM | `brighteyes/brighteyes_capability_spec.md`; `brighteyes/brighteyes_specification.md` |
| Evidence Critic TPM | 项目证据索引、领域 Agent 结果和冲突记录；不默认加载领域知识 |
| Version Fit TPM | 两份产品版本说明和能力规格总则 |
| Site Adaptation TPM | 已确认风险、能力规格和项目现场资料 |
| Nonstandard Classifier TPM | 已确认交付项、能力规格总则和版本说明 |
| Effort Estimation TPM | `delivery_baselines/effort_estimation_baseline.md` |
| Global Summary TPM | 前序 Agent 结构化结果；不重新进行领域判断 |

## Runtime Rules

- Worker 只加载本角色白名单内的文件。
- 明眸知识仅在项目出现明眸触发信号时加载。
- 任何知识条目都不能替代当前项目证据。
- 文件缺失时必须记录知识覆盖缺口，不得静默推断。
