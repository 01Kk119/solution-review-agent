# 数据契约

所有结果使用 UTF-8 JSON。`schema_version` 当前为 `2.1`。结论必须携带证据、依据类型和置信度；缺少权威基线时必须显式降级为待确认或不可估算。

## GatewayContext

```json
{
  "project_key": "vn26099_example",
  "request_id": "req-...",
  "trace_id": "review-20260724-...",
  "current_request": "对该项目做多 Agent 风险评审并生成交付建议",
  "input_paths": {
    "package": "C:/.../project_requirement_package.md",
    "evidence_index": "C:/.../evidence_index.json",
    "missing_info": "C:/.../missing_info_checklist.md",
    "metadata": "C:/.../metadata.json",
    "version_matrix": "C:/.../product_version_matrix.json",
    "effort_baseline": "C:/.../effort_baseline.json"
  },
  "attachments": [
    {
      "name": "Application Form.xlsx",
      "path": "C:/.../Application Form.xlsx",
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "size_bytes": 405773,
      "sha256": "...",
      "parse_status": "extracted",
      "content_ref": "parsed_sources.md#file-1"
    }
  ],
  "allow_write": true
}
```

`version_matrix` 和 `effort_baseline` 可以缺失；缺失时不允许生成伪精确版本或人时。每个当前项目附件必须显式列入 `attachments`。只要列表非空，就不得声称未收到原始资料；单文件解析失败应使用 `parse_status=parse_failed`，并继续处理其他附件。

## TaskPlan

```json
{
  "level": "L3",
  "rationale": "完整项目，包含风险识别和交付决策",
  "confidence": 0.9,
  "trace_id": "review-20260724-...",
  "stages": [
    {
      "name": "domain_review",
      "tasks": [
        {
          "task_id": "t-nav",
          "agent": "navigation_control_tpm",
          "intent": "识别导航、定位和控制风险",
          "params": {},
          "context_hint": {"package_sections": ["3", "5", "9", "11"]},
          "read_only": true,
          "depends_on": []
        }
      ]
    },
    {
      "name": "delivery_decision",
      "tasks": [
        {
          "task_id": "t-version",
          "agent": "version_fit_tpm",
          "intent": "提出版本建议并披露能力差距",
          "params": {},
          "context_hint": {},
          "read_only": true,
          "depends_on": ["t-critic"]
        }
      ]
    }
  ]
}
```

## AgentResult

```json
{
  "schema_version": "2.1",
  "task_id": "t-mm",
  "agent": "mingmou_risk_tpm",
  "domain": "mingmou",
  "status": "completed",
  "summary": "识别 3 项当前风险、2 项待确认",
  "risks": [
    {
      "risk_id": "MM-001",
      "domain": "mingmou",
      "title": "示例风险",
      "statement": "项目事实与产品边界之间存在待确认差异。",
      "status": "pending_confirmation",
      "severity": "中",
      "basis_type": "AI推断待确认",
      "evidence_refs": ["E012"],
      "impact": "可能影响识别覆盖和验收。",
      "recommendation": "设计冻结前完成现场视野仿真与实测。",
      "owner": "算法/方案",
      "confidence": 0.75,
      "handoff_to": ["software_rcs_interface_tpm"]
    }
  ],
  "open_questions": [
    {
      "question_id": "SITE-PEND-001",
      "category": "site_adaptation_pending",
      "question": "请确认相机安装高度和遮挡边界。",
      "related_risk_ids": ["MM-001"],
      "provisional_severity": "中",
      "owner": "客户/方案",
      "close_by": "设计冻结前"
    }
  ],
  "handoffs": [],
  "warnings": [],
  "tool_calls_made": [],
  "tokens_used": 0
}
```

允许的 AgentResult `status`：

- `completed`
- `partial`
- `failed`
- `not_applicable`

每个风险的 `severity` 只能为 `高`、`中`、`低`。信息不全时仍需给出暂定等级并降低 `confidence`；影响能力满足度或新功能判断的缺失条件使用 `open_questions.category=site_adaptation_pending`，且必须引用关联风险及其暂定等级。

允许的风险 `status`：

- `current_risk`
- `pending_confirmation`
- `scope_change_warning`
- `not_applicable`

## CriticResult

```json
{
  "schema_version": "2.1",
  "agent": "evidence_critic_tpm",
  "status": "completed",
  "unsupported_risks": [],
  "conditional_inference_misuse": [],
  "duplicate_groups": [],
  "fact_conflicts": [],
  "severity_conflicts": [],
  "boundary_violations": [],
  "missing_agents": [],
  "recommendations": []
}
```

## VersionRecommendationResult

保存为 `<trace_dir>/decision_results/version_fit_tpm.json`。

```json
{
  "schema_version": "2.2",
  "agent": "version_fit_tpm",
  "status": "completed",
  "baseline_status": "available",
  "unified_version": "5.3.2",
  "version_risk_level": "中",
  "fit_5_2_2": "否",
  "fit_5_3_2": "是",
  "system_recommendations": [
    {
      "system": "vehicle",
      "status": "applicable",
      "release_type": "年度版本/研发创新版",
      "factory_version": "5.2.2",
      "onsite_target_version": "5.3.2",
      "recommendation_type": "upgrade_onsite",
      "capability_reason": "满足声光规则配置",
      "dependencies": ["Robotune 调试权限"],
      "validation_plan": "到场后按声光规则用例验证",
      "rollback_plan": "保留出厂版本包与配置快照",
      "evidence_refs": ["REQ-001", "VER-023"],
      "confidence": 0.8
    }
  ],
  "alternatives": [],
  "capability_matches": [
    {
      "requirement_id": "REQ-001",
      "capability": "库位状态接入",
      "fit": "version_dependent",
      "system": "mingmou",
      "evidence_refs": ["E001", "VER-023"],
      "notes": ""
    }
  ],
  "gaps": [],
  "assumptions": [],
  "approval_required_by": ["版本负责人", "软件负责人"],
  "confidence": 0.8
}
```

`system` 建议使用 `vehicle`、`rcs`、`mingmou` 或经批准的产品系统标识。`status` 只能为 `applicable` 或 `not_applicable`。`recommendation_type` 只能为 `keep_factory`、`upgrade_onsite`、`direct_target`、`insufficient_evidence` 或 `not_applicable`。

`unified_version` 是项目唯一目标版本，只能为 `5.2.2`、`5.3.2`、`暂无标准版本可满足` 或 `待确认`。所有适用系统的 `onsite_target_version` 必须与其一致，不得按模块拆分或混用版本。风险映射固定为：`5.2.2/低`、`5.3.2/中`、`暂无标准版本可满足/高`、`待确认/待确认`。

`baseline_status`：`available`、`partial`、`missing`。当为 `missing` 时，每个适用系统的 `factory_version` 和 `onsite_target_version` 必须为“待版本负责人确认”，`recommendation_type` 必须为 `insufficient_evidence`。版本 Agent 只给版本适配建议，不输出非标结论或人时。

## NonstandardResult

保存为 `<trace_dir>/decision_results/nonstandard_classifier_tpm.json`。

```json
{
  "schema_version": "2.1",
  "agent": "nonstandard_classifier_tpm",
  "status": "completed",
  "baseline_status": "available",
  "items": [
    {
      "item_id": "DEL-001",
      "title": "新增明眸告警状态映射",
      "module": "RCS/接口",
      "classification": "nonstandard_development",
      "requirement_refs": ["REQ-001"],
      "risk_refs": ["SW-002", "MM-001"],
      "evidence_refs": ["E001"],
      "implementation_method": "新增接口字段与状态机",
      "standard_boundary": "推荐版本不含该状态映射",
      "justification": "项目要求新增产品能力",
      "deliverable": "接口字段、状态机和测试记录",
      "acceptance_criteria": "告警状态按确认的信号表闭环",
      "close_condition": "接口联调和异常恢复测试通过",
      "dependencies": [],
      "owner_role": "软件/RCS",
      "version_strategy": "补丁版本或项目分支，待版本负责人确认",
      "approval_required_by": ["版本负责人", "研发负责人"],
      "confidence": 0.75
    }
  ],
  "custom_development_item_ids": ["DEL-001"],
  "nonstandard_item_ids": ["DEL-001"],
  "pending_classification": [],
  "out_of_scope_item_ids": [],
  "warnings": []
}
```

`classification` 只能是 `standard_capability`、`standard_configuration`、`version_dependent_configuration`、`custom_development`、`nonstandard_development`、`pending_confirmation` 或 `out_of_scope`。

- `custom_development_item_ids` 只能引用 `custom_development` 或 `nonstandard_development` 项；
- `nonstandard_item_ids` 只能引用 `nonstandard_development` 项；
- 硬件选型、EHS、安全认证、土建、施工和一般现场整改使用 `out_of_scope`，不进入开发附件，也不继续评估；
- 缺少版本基线时不得输出 `nonstandard_development`，只能保留 `pending_confirmation`。

## EffortEstimateResult

保存为 `<trace_dir>/decision_results/effort_estimation_tpm.json`。单位统一为人时，`8 人时 = 1 人日`。

```json
{
  "schema_version": "2.1",
  "agent": "effort_estimation_tpm",
  "status": "completed",
  "baseline_status": "available",
  "unit": "person_hour",
  "items": [
    {
      "item_id": "EST-001",
      "source_agent": "nonstandard_classifier_tpm",
      "source_item_id": "DEL-001",
      "title": "新增明眸告警状态映射",
      "estimate_status": "estimated",
      "role_hours": [
        {"phase": "开发", "role": "软件/RCS", "low": 16, "likely": 24, "high": 40},
        {"phase": "测试", "role": "测试", "low": 8, "likely": 16, "high": 24}
      ],
      "total_hours": {"low": 24, "likely": 40, "high": 64},
      "estimate_basis": ["BASE-014", "专家复核"],
      "assumptions": ["信号表在开发前冻结"],
      "exclusions": ["客户现场等待时间"],
      "confidence": 0.65
    }
  ],
  "totals": {"low": 24, "likely": 40, "high": 64},
  "unestimated_items": [],
  "approval_required_by": ["研发负责人", "TPM"],
  "warnings": []
}
```

`source_agent` 只能为 `nonstandard_classifier_tpm`；相应 `source_item_id` 必须指向已存在且由 VisionNav 承担的功能工作项。硬件、EHS、安全认证、土建、现场整改、客户工作和等待时间全部排除。

缺少历史基线或必要输入时，`estimate_status` 使用 `not_estimable`，保留在 `unestimated_items`，并说明缺失信息与确认责任人。不得用 0 代替不可估算。

## FinalManifest

```json
{
  "schema_version": "2.1",
  "project_key": "vn26099_example",
  "trace_id": "review-20260724-...",
  "execution_mode": "multi_agent",
  "completed_agents": [],
  "failed_agents": [],
  "not_applicable_agents": [],
  "decision_agents": {
    "version_fit_tpm": "completed",
    "nonstandard_classifier_tpm": "completed",
    "effort_estimation_tpm": "partial"
  },
  "conflict_count": 0,
  "current_risk_count": 0,
  "pending_confirmation_count": 0,
  "scope_change_warning_count": 0,
  "overall_risk_level": "中",
  "output_files": [
    "review_analysis.md",
    "review_analysis.html",
    "version_recommendation.md",
    "version_recommendation.html",
    "custom_development_checklist.md",
    "custom_development_checklist.html",
    "nonstandard_development_items.md",
    "nonstandard_development_items.html",
    "effort_recommendation.md",
    "effort_recommendation.html"
  ],
  "approval_status": {
    "version": "pending_version_owner",
    "nonstandard": "pending_engineering_owner",
    "effort": "pending_tpm_and_engineering"
  }
}
```
