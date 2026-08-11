---
name: multi-agent-risk-review
description: 编排 VisionNav 叉车、AGV、AMR 项目的多 Agent 非标准功能开发风险识别与交付决策。用于跨取放、导航控制、调度效率、软件/RCS/接口及条件明眸评审，并生成方案评审主报告及版本适配、定制化开发、非标判定、人时估算四份独立附件。
---

# 多 Agent 风险评审

## 目标

把结构化项目资料包作为唯一事实入口，按“计划 → 领域风险识别 → 证据质检 → 交付决策准备 → 全局汇总”执行评审。风险事实与版本、人时等交付决策分开生成，所有中间结果使用结构化契约并保存在独立 trace 目录。

本 Skill 编排六层：

1. Gateway：建立项目、请求、trace 和权限上下文。
2. Planner：生成结构化 `TaskPlan`。
3. Runner：按依赖图调度只读 Agent，限制并发，隔离失败。
4. Domain Workers：在各自领域返回 `AgentResult`。
5. Evidence Critic 与 Decision Agents：质检证据，分别生成版本适配、非标分类和人时估算结果。
6. Global Summary TPM：唯一写入者，生成一份主报告、四份独立附件及 trace 汇总。

开始前读取：

- `references/architecture.md`
- `references/agent-roster.yaml`
- `references/data-contracts.md`
- `references/domain-agent-prompts.md`
- `references/decision-agent-design.md`
- 生成方案未决项时读取 `references/solution-unresolved-items.md`
- 涉及版本判断时必须读取 `references/version-package-policy.md`

## 输入

优先读取：

- `project_requirement_package.md`
- `evidence_index.json`
- `missing_info_checklist.md`
- `metadata.json`

交付决策还应读取：

- 产品版本能力矩阵或当前发布基线；
- 历史工时基线或经授权的专家估算规则。

版本或工时基线缺失不阻止风险评审，但必须把相应结论降级为待确认或不可估算。只在核验证据或结构化资料包明确声明解析缺口时读取原始项目文件。

## 复杂度路由

- 单一、明确的明眸问题：直接路由到 `$mingmou-risk-tpm`。
- 单一其他领域问题：只启动对应领域 Agent。
- 完整项目评审或要求输出交付文件：使用完整 L3 多 Agent 计划。
- Planner 无法解析：回退到取放、导航、调度、软件四个核心领域 Agent、Evidence Critic、三个交付决策 Agent 和 Global Summary；明眸仅在触发时增加，并在 manifest 声明回退。

## 标准流程

### 1. 建立 GatewayContext

记录 `project_key`、`request_id`、`trace_id`、用户请求、每个附件的绝对路径/类型/大小/哈希/解析状态和 `allow_write`。身份、项目路径和 trace 只能从该上下文派生，不能让 Worker 从隐式会话状态推断。只要附件清单非空，就不能声称未收到原始资料；解析失败必须按文件披露。

### 2. 生成 TaskPlan

Planner 必须输出结构化 JSON，至少包含：

- 复杂度等级和理由；
- 启动的 Agent；
- 每个任务的输入切片、只读标记和依赖；
- 串行阶段顺序。

保存到：

```text
<ProjectOutputDir>/agent_trace/<trace_id>/plan.json
```

随后执行轻量需求建模，只生成附件解析摘要、关键字段、实际出现的同义词映射、短 `REQ-*`—证据索引、冲突和缺失清单。禁止让模型重写整份项目资料、扩写背景或提前生成风险结论。

### 3. 运行领域 Agent

领域 Worker 全部只读，最多同时运行 2 个。每个请求独立使用 120 秒超时和最多 1 次重试；单个 Agent 超时或失败时保存失败结果和覆盖缺口，其他 Agent 继续。每个 Worker 只接收自己的角色提示词、`AgentTask`、相关资料章节和必要证据索引，结果必须符合 `AgentResult`：

领域结果完成后只允许一轮跨 Agent 问答。每个 Agent 在整个评审中最多提 1 个问题，只能选择最可能需要新增或修改产品功能的问题；没有该类问题则不提问，回答不得触发追问。

```text
<trace_dir>/agent_results/<agent_name>.json
```

领域 Agent：

- `pick_place_tpm`
- `navigation_control_tpm`
- `dispatch_efficiency_tpm`
- `software_rcs_interface_tpm`
- `mingmou_risk_tpm`（条件触发，使用 `$mingmou-risk-tpm`）

### 4. 运行 Evidence Critic

领域结果齐备后，检查：

- 风险是否有项目证据；
- 条件性推断是否被误写为当前风险；
- 重复风险、事实冲突、严重度冲突；
- evidence_index 定位是否存在；
- Worker 是否越过领域边界。

保存为 `<trace_dir>/critic_result.json`。不得静默删除冲突。

### 5. 运行交付决策 Agent

所有 Agent 仍为只读，结果写入：

```text
<trace_dir>/decision_results/
  version_fit_tpm.json
  nonstandard_classifier_tpm.json
  effort_estimation_tpm.json
```

依赖顺序：

1. `version_fit_tpm` 在 Critic 后运行；
2. `nonstandard_classifier_tpm` 等待版本结果，只对已有功能交付项分类；
3. `effort_estimation_tpm` 等待版本和非标结果，只估算有稳定来源 ID 的功能工作项。

约束：

- 版本适配 TPM 统一选择项目级完整版本包；模块只分别提供能力证据，不得分别指定版本；
- 5.2.2满足全部需求为低风险；需统一升级5.3.2为中风险；5.3.2仍不能满足为高风险；
- 非标判定对已有交付项分类，不新增需求，不设置“定制范围 TPM”；
- 非标开发项只是确认超出标准版本边界且需要修改产品能力的子集；
- 推荐人时使用低/最可能/高区间，按角色拆分，并披露不可估项。
- 硬件、EHS、安全认证、土建、施工和一般现场整改均为评审范围外。

### 6. 全局汇总并写最终文档

使用 `$global-summary-tpm`。它只在全部只读阶段结束后串行写：

```text
<ProjectOutputDir>/review_analysis.md
<ProjectOutputDir>/review_analysis.html
<ProjectOutputDir>/version_recommendation.md
<ProjectOutputDir>/version_recommendation.html
<ProjectOutputDir>/custom_development_checklist.md
<ProjectOutputDir>/custom_development_checklist.html
<ProjectOutputDir>/nonstandard_development_items.md
<ProjectOutputDir>/nonstandard_development_items.html
<ProjectOutputDir>/effort_recommendation.md
<ProjectOutputDir>/effort_recommendation.html
<trace_dir>/final_risk_register.json
<trace_dir>/final_manifest.json
```

五份 Markdown 是审计源，五份 HTML 是用户可读交付件；两种格式必须逐项一致，并使用 `global-summary-tpm/assets/` 中的模板与统一 HTML 外壳。导出时使用 `<项目编号>项目-<文档名称>.html` 的易读名称。版本、人时和非标结论是带依据和置信度的建议，不是最终承诺；最终承诺必须经过相应负责人审批。

### 可见产物表达

- 直接从标题、表头或第一条结论开始。
- 禁止寒暄、角色自述、任务复述、资料接收说明、处理过程和完成宣告。
- 禁止使用“好的”“作为某某 Agent/TPM”“我已根据”“我已生成”“以下是”等开场话术。

### 7. 校验

运行：

```powershell
python ".\01_Agent程序与知识库\Agent工作区\skills\multi-agent-risk-review\scripts\validate_agent_artifacts.py" `
  --trace-dir "<trace_dir>" `
  --output-dir "<ProjectOutputDir>"
```

校验失败必须修复后重跑。

### 8. 导出和登记

沿用 `solution-review` 的导出与登记流程：

- 导出到 `<OriginalProjectDir>/评估结果/`
- 登记到 `项目汇总包/project_index.csv`

`agent_trace/` 是过程记录，不写入可见对话历史，也不展开复制进跨项目 CSV。

## 权限与并发

- Planner、领域 Worker、Evidence Critic、三个 Decision Agent：只读。
- Global Summary TPM：只能写 ProjectOutputDir 中声明的最终文件和当前 trace 汇总。
- 所有写入串行执行。
- ToolExecutor 必须按 `agent-roster.yaml` 集中限制工具和权限，不能只依赖提示词。
- 不允许任何只读 Agent 修改原始资料、结构化资料包或共享项目索引。

## 证据规则

允许的依据类型：

- `原文明确`
- `会议口头信息`
- `AI归类`
- `AI推断待确认`
- `条件性推断`
- `无原文依据-不列为当前风险`

`条件性推断` 只能进入范围变更提醒，不能提高当前风险等级。没有项目证据的领域知识只能用于提出待确认问题。版本能力矩阵和历史工时基线也必须有可追溯 ID。

## 失败处理

- 单个领域 Worker 失败：保留其他结果，最终文档披露覆盖缺口。
- 明眸未触发：明眸章节写“未发现触发依据/不适用”。
- 版本基线缺失：版本写“待版本负责人确认”，非标仅保留待确认判定。
- 工时基线缺失：对应项写“不可可靠估算”，不得用 0 或伪精确值代替。
- 证据冲突：并列冲突值和来源，列入待确认。
- 不支持子 Agent：按相同 AgentSpec 顺序执行并生成独立结果，在 manifest 标记 `single_agent_fallback`。
