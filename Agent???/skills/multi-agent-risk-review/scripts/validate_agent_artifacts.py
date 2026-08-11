from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_AGENT_STATUSES = {"completed", "partial", "failed", "not_applicable"}
ALLOWED_RISK_STATUSES = {
    "current_risk",
    "pending_confirmation",
    "scope_change_warning",
    "not_applicable",
}
ALLOWED_SEVERITIES = {"低", "中", "高"}
ALLOWED_BASIS_TYPES = {
    "原文明确",
    "会议口头信息",
    "AI归类",
    "AI推断待确认",
    "条件性推断",
    "无原文依据-不列为当前风险",
}
ALLOWED_DELIVERY_CLASSIFICATIONS = {
    "standard_capability",
    "standard_configuration",
    "version_dependent_configuration",
    "custom_development",
    "nonstandard_development",
    "pending_confirmation",
    "out_of_scope",
}
DECISION_AGENTS = {
    "version_fit_tpm",
    "nonstandard_classifier_tpm",
    "effort_estimation_tpm",
}
REQUIRED_RISK_FIELDS = {
    "risk_id",
    "domain",
    "title",
    "statement",
    "status",
    "severity",
    "basis_type",
    "evidence_refs",
    "impact",
    "recommendation",
    "owner",
    "confidence",
    "handoff_to",
}

REQUIRED_HEADINGS = [
    "## 总评价",
    "## 项目概览",
    "## 应用场景与边界",
    "## 分领域评估",
    "## 版本评估",
    "## 风险、冲突与待确认",
    "## 现场适配待确认清单",
    "## 下一步动作",
    "## Agent 覆盖与审批状态",
]
RISK_TABLE_HEADER = "| ID | 风险/待确认 | 风险等级 | 依据类型 | 影响 | 证据/出处 | 建议动作 | 负责人 |"

OUTPUT_SPECS = {
    "review_analysis.md": {
        "headings": REQUIRED_HEADINGS,
        "headers": [
            RISK_TABLE_HEADER,
            "| ID | 所属领域 | 待确认条件 | 关联风险 | 当前暂定等级 | 责任方 | 关闭时间 |",
        ],
    },
    "version_recommendation.md": {
        "headings": [
            "## 推荐结论",
            "## 分系统版本建议",
            "## 需求能力适配矩阵",
            "## 差距与替代方案",
            "## 假设与限制",
            "## 审批状态",
        ],
        "headers": [
            "| 系统 | 版本类型 | 出厂版本 | 到场目标版本 | 推荐动作 | 能力理由 | 依赖/验证 | 依据 |",
            "| 需求/能力 | 所属系统 | 项目要求 | 支持情况 | 差距/处理 | 依据 |",
        ],
    },
    "custom_development_checklist.md": {
        "headings": [
            "## 口径说明",
            "## A. 已确认定制开发项",
            "## B. 版本依赖配置项（不计为定制开发）",
            "## C. 标准能力项",
            "## 待确认与排除项",
        ],
        "headers": [
            "| ID | 定制项 | 需求与边界 | 拟采用方案 | 可交付物 | 关闭条件 | 责任角色 | 依据 |",
            "| ID | 功能项 | 分类 | 实现方式 | 版本条件 | 验收标准 | 依据 |",
            "| 功能 | 实现方式 | 评估 | 交付关注点 | 依据 |",
        ],
    },
    "nonstandard_development_items.md": {
        "headings": [
            "## 判定口径",
            "## 已确认非标开发项",
            "## 待判定项",
            "## 非非标项说明",
            "## 审批状态",
        ],
        "headers": [
            "| ID | 非标内容 | 所属模块 | 标准能力边界 | 判定理由 | 版本策略 | 交付物/验收 | 依据 | 审批人 |"
        ],
    },
    "effort_recommendation.md": {
        "headings": [
            "## 估算口径",
            "## 分项人时",
            "## 角色汇总",
            "## 不可估算项",
            "## 假设与不包含项",
            "## 审批状态",
        ],
        "headers": [
            "| 来源项 ID | 工作项 | 阶段 | 角色 | 低 | 最可能 | 高 | 估算依据 | 假设/不包含项 | 置信度 |",
            "| 角色 | 低（人时） | 最可能（人时） | 高（人时） |",
        ],
    },
}

HTML_OUTPUT_SPECS = {
    "review_analysis.html": ["总评价", "项目概览", "分领域评估", "版本评估"],
    "version_recommendation.html": ["版本适配", "出厂版本", "到场目标版本"],
    "custom_development_checklist.html": ["定制化开发", "版本依赖", "标准能力"],
    "nonstandard_development_items.html": ["非标判定", "标准能力边界", "待判定"],
    "effort_recommendation.html": ["人时估算", "最可能", "不可估算"],
}


def load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"缺少 JSON 文件: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"无法解析 JSON {path}: {exc}")
        return None


def require_fields(
    value: Any, fields: set[str] | tuple[str, ...], source: str, errors: list[str]
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{source}: 必须是对象")
        return False
    missing = sorted(set(fields) - set(value))
    if missing:
        errors.append(f"{source}: 缺少字段 {', '.join(missing)}")
        return False
    return True


def validate_confidence(value: Any, source: str, errors: list[str]) -> None:
    if not isinstance(value, (int, float)) or not 0 <= value <= 1:
        errors.append(f"{source}: confidence 必须在 0 到 1 之间")


def validate_range(value: Any, source: str, errors: list[str]) -> None:
    if not require_fields(value, {"low", "likely", "high"}, source, errors):
        return
    low, likely, high = value["low"], value["likely"], value["high"]
    if not all(isinstance(item, (int, float)) and item >= 0 for item in (low, likely, high)):
        errors.append(f"{source}: low/likely/high 必须是非负数")
    elif not low <= likely <= high:
        errors.append(f"{source}: 必须满足 low <= likely <= high")


def validate_risk(
    risk: Any,
    source: str,
    errors: list[str],
    seen_ids: set[str],
) -> None:
    if not require_fields(risk, REQUIRED_RISK_FIELDS, source, errors):
        return

    risk_id = str(risk["risk_id"]).strip()
    if not risk_id:
        errors.append(f"{source}: risk_id 不能为空")
    elif risk_id in seen_ids:
        errors.append(f"{source}: risk_id 重复: {risk_id}")
    else:
        seen_ids.add(risk_id)

    status = risk["status"]
    basis_type = risk["basis_type"]
    evidence_refs = risk["evidence_refs"]
    if status not in ALLOWED_RISK_STATUSES:
        errors.append(f"{source}/{risk_id}: 非法风险状态 {status}")
    if risk["severity"] not in ALLOWED_SEVERITIES:
        errors.append(f"{source}/{risk_id}: 非法严重度 {risk['severity']}")
    if basis_type not in ALLOWED_BASIS_TYPES:
        errors.append(f"{source}/{risk_id}: 非法依据类型 {basis_type}")
    if not isinstance(evidence_refs, list):
        errors.append(f"{source}/{risk_id}: evidence_refs 必须是数组")
    elif status in {"current_risk", "pending_confirmation"} and not evidence_refs:
        errors.append(f"{source}/{risk_id}: 当前/待确认风险必须提供证据定位")
    if basis_type == "条件性推断" and status != "scope_change_warning":
        errors.append(f"{source}/{risk_id}: 条件性推断只能是 scope_change_warning")
    if (
        basis_type == "无原文依据-不列为当前风险"
        and status in {"current_risk", "pending_confirmation"}
    ):
        errors.append(f"{source}/{risk_id}: 无原文依据不得列为当前/待确认风险")
    if not isinstance(risk["handoff_to"], list):
        errors.append(f"{source}/{risk_id}: handoff_to 必须是数组")
    validate_confidence(risk["confidence"], f"{source}/{risk_id}", errors)


def validate_version_result(data: Any, source: str, errors: list[str]) -> None:
    fields = {
        "schema_version",
        "agent",
        "status",
        "baseline_status",
        "system_recommendations",
        "alternatives",
        "capability_matches",
        "gaps",
        "assumptions",
        "approval_required_by",
        "confidence",
    }
    if not require_fields(data, fields, source, errors):
        return
    if data["agent"] != "version_fit_tpm":
        errors.append(f"{source}: agent 必须是 version_fit_tpm")
    if data["status"] not in ALLOWED_AGENT_STATUSES:
        errors.append(f"{source}: 非法状态 {data['status']}")
    if data["baseline_status"] not in {"available", "partial", "missing"}:
        errors.append(f"{source}: 非法 baseline_status {data['baseline_status']}")
    if str(data.get("schema_version", "")) >= "2.2":
        unified_fields = {
            "unified_version",
            "version_risk_level",
            "fit_5_2_2",
            "fit_5_3_2",
        }
        if require_fields(data, unified_fields, source, errors):
            mapping = {
                ("是", "未评估"): ("5.2.2", "低"),
                ("是", "是"): ("5.2.2", "低"),
                ("否", "是"): ("5.3.2", "中"),
                ("否", "否"): ("暂无标准版本可满足", "高"),
                ("待确认", "待确认"): ("待确认", "待确认"),
            }
            expected = mapping.get((data["fit_5_2_2"], data["fit_5_3_2"]))
            actual = (data["unified_version"], data["version_risk_level"])
            if expected is None:
                errors.append(f"{source}: 5.2.2/5.3.2满足状态组合不合法")
            elif actual != expected:
                errors.append(
                    f"{source}: 统一版本与风险等级映射错误，应为 {expected[0]}/{expected[1]}"
                )
    for field in (
        "system_recommendations",
        "alternatives",
        "capability_matches",
        "gaps",
        "assumptions",
        "approval_required_by",
    ):
        if not isinstance(data[field], list):
            errors.append(f"{source}: {field} 必须是数组")
    if isinstance(data["system_recommendations"], list):
        system_fields = {
            "system",
            "status",
            "release_type",
            "factory_version",
            "onsite_target_version",
            "recommendation_type",
            "capability_reason",
            "dependencies",
            "validation_plan",
            "rollback_plan",
            "evidence_refs",
            "confidence",
        }
        allowed_types = {
            "keep_factory",
            "upgrade_onsite",
            "direct_target",
            "insufficient_evidence",
            "not_applicable",
        }
        for index, item in enumerate(data["system_recommendations"], start=1):
            item_source = f"{source}/system_recommendations[{index}]"
            if not require_fields(item, system_fields, item_source, errors):
                continue
            if item["status"] not in {"applicable", "not_applicable"}:
                errors.append(f"{item_source}: 非法 status {item['status']}")
            if item["recommendation_type"] not in allowed_types:
                errors.append(
                    f"{item_source}: 非法 recommendation_type {item['recommendation_type']}"
                )
            if data["baseline_status"] == "missing" and item["status"] == "applicable":
                if (
                    item["factory_version"] != "待版本负责人确认"
                    or item["onsite_target_version"] != "待版本负责人确认"
                ):
                    errors.append(f"{item_source}: 缺少版本基线时不得给出具体推荐版本")
                if item["recommendation_type"] != "insufficient_evidence":
                    errors.append(
                        f"{item_source}: 缺少版本基线时 recommendation_type 必须为 insufficient_evidence"
                    )
            if (
                str(data.get("schema_version", "")) >= "2.2"
                and item["status"] == "applicable"
                and data.get("unified_version") not in {"暂无标准版本可满足", "待确认"}
                and item["onsite_target_version"] != data.get("unified_version")
            ):
                errors.append(f"{item_source}: 到场目标版本必须与项目统一版本一致")
            for field in ("dependencies", "evidence_refs"):
                if not isinstance(item[field], list):
                    errors.append(f"{item_source}: {field} 必须是数组")
            validate_confidence(item["confidence"], item_source, errors)
    validate_confidence(data["confidence"], source, errors)


def validate_delivery_items(
    items: Any, source: str, baseline_status: str, errors: list[str]
) -> tuple[set[str], dict[str, str]]:
    item_ids: set[str] = set()
    classifications: dict[str, str] = {}
    if not isinstance(items, list):
        errors.append(f"{source}: 必须是数组")
        return item_ids, classifications
    item_fields = {
        "item_id",
        "title",
        "module",
        "classification",
        "requirement_refs",
        "risk_refs",
        "evidence_refs",
        "implementation_method",
        "standard_boundary",
        "justification",
        "deliverable",
        "acceptance_criteria",
        "close_condition",
        "dependencies",
        "owner_role",
        "version_strategy",
        "approval_required_by",
        "confidence",
    }
    for index, item in enumerate(items, start=1):
        item_source = f"{source}[{index}]"
        if not require_fields(item, item_fields, item_source, errors):
            continue
        item_id = str(item["item_id"]).strip()
        if not item_id or item_id in item_ids:
            errors.append(f"{item_source}: item_id 为空或重复")
        else:
            item_ids.add(item_id)
            classifications[item_id] = item["classification"]
        if item["classification"] not in ALLOWED_DELIVERY_CLASSIFICATIONS:
            errors.append(
                f"{item_source}: 非法 classification {item['classification']}"
            )
        if (
            baseline_status == "missing"
            and item["classification"] == "nonstandard_development"
        ):
            errors.append(f"{item_source}: 缺少版本基线时不得确认非标")
        for field in (
            "requirement_refs",
            "risk_refs",
            "evidence_refs",
            "dependencies",
            "approval_required_by",
        ):
            if not isinstance(item[field], list):
                errors.append(f"{item_source}: {field} 必须是数组")
        validate_confidence(item["confidence"], item_source, errors)
    return item_ids, classifications


def validate_nonstandard_result(
    data: Any, source: str, errors: list[str]
) -> set[str]:
    fields = {
        "schema_version",
        "agent",
        "status",
        "baseline_status",
        "items",
        "custom_development_item_ids",
        "nonstandard_item_ids",
        "pending_classification",
        "out_of_scope_item_ids",
        "warnings",
    }
    if not require_fields(data, fields, source, errors):
        return set()
    if data["agent"] != "nonstandard_classifier_tpm":
        errors.append(f"{source}: agent 必须是 nonstandard_classifier_tpm")
    if data["status"] not in ALLOWED_AGENT_STATUSES:
        errors.append(f"{source}: 非法状态 {data['status']}")
    if data["baseline_status"] not in {"available", "partial", "missing"}:
        errors.append(f"{source}: 非法 baseline_status {data['baseline_status']}")
    item_ids, classifications = validate_delivery_items(
        data["items"],
        f"{source}/items",
        data["baseline_status"],
        errors,
    )
    for field in (
        "custom_development_item_ids",
        "nonstandard_item_ids",
        "pending_classification",
        "out_of_scope_item_ids",
        "warnings",
    ):
        if not isinstance(data[field], list):
            errors.append(f"{source}: {field} 必须是数组")
    if isinstance(data["custom_development_item_ids"], list):
        for item_id in data["custom_development_item_ids"]:
            if classifications.get(item_id) not in {
                "custom_development",
                "nonstandard_development",
            }:
                errors.append(
                    f"{source}: custom_development_item_ids 引用了非开发项 {item_id}"
                )
    if isinstance(data["nonstandard_item_ids"], list):
        for item_id in data["nonstandard_item_ids"]:
            if classifications.get(item_id) != "nonstandard_development":
                errors.append(
                    f"{source}: nonstandard_item_ids 引用了非非标项 {item_id}"
                )
    return item_ids


def validate_effort_result(
    data: Any,
    source: str,
    delivery_ids: set[str],
    errors: list[str],
) -> None:
    fields = {
        "schema_version",
        "agent",
        "status",
        "baseline_status",
        "unit",
        "items",
        "totals",
        "unestimated_items",
        "approval_required_by",
        "warnings",
    }
    if not require_fields(data, fields, source, errors):
        return
    if data["agent"] != "effort_estimation_tpm":
        errors.append(f"{source}: agent 必须是 effort_estimation_tpm")
    if data["status"] not in ALLOWED_AGENT_STATUSES:
        errors.append(f"{source}: 非法状态 {data['status']}")
    if data["baseline_status"] not in {"available", "partial", "missing"}:
        errors.append(f"{source}: 非法 baseline_status {data['baseline_status']}")
    if data["unit"] != "person_hour":
        errors.append(f"{source}: unit 必须是 person_hour")
    validate_range(data["totals"], f"{source}/totals", errors)
    if not isinstance(data["items"], list):
        errors.append(f"{source}: items 必须是数组")
        return
    item_fields = {
        "item_id",
        "source_agent",
        "source_item_id",
        "title",
        "estimate_status",
        "role_hours",
        "total_hours",
        "estimate_basis",
        "assumptions",
        "exclusions",
        "confidence",
    }
    for index, item in enumerate(data["items"], start=1):
        item_source = f"{source}/items[{index}]"
        if not require_fields(item, item_fields, item_source, errors):
            continue
        source_agent = item["source_agent"]
        source_ids = delivery_ids if source_agent == "nonstandard_classifier_tpm" else set()
        if source_agent != "nonstandard_classifier_tpm":
            errors.append(f"{item_source}: 非法 source_agent {source_agent}")
        elif item["source_item_id"] not in source_ids:
            errors.append(f"{item_source}: source_item_id 未指向有效来源工作项")
        if item["estimate_status"] not in {"estimated", "not_estimable"}:
            errors.append(f"{item_source}: 非法 estimate_status {item['estimate_status']}")
        if item["estimate_status"] == "estimated":
            validate_range(item["total_hours"], f"{item_source}/total_hours", errors)
        if not isinstance(item["role_hours"], list):
            errors.append(f"{item_source}: role_hours 必须是数组")
        else:
            for role_index, role_hours in enumerate(item["role_hours"], start=1):
                role_source = f"{item_source}/role_hours[{role_index}]"
                if require_fields(
                    role_hours,
                    {"phase", "role", "low", "likely", "high"},
                    role_source,
                    errors,
                ):
                    validate_range(role_hours, role_source, errors)
        for field in ("estimate_basis", "assumptions", "exclusions"):
            if not isinstance(item[field], list):
                errors.append(f"{item_source}: {field} 必须是数组")
        validate_confidence(item["confidence"], item_source, errors)


def validate_output_file(path: Path, spec: dict[str, list[str]], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"缺少最终文档: {path}")
        return
    text = path.read_text(encoding="utf-8-sig")
    for heading in spec["headings"]:
        if heading not in text:
            errors.append(f"{path.name} 缺少标题: {heading}")
    for header in spec["headers"]:
        if header not in text:
            errors.append(f"{path.name} 表头不符合模板: {header}")
    if "{{" in text or "}}" in text:
        errors.append(f"{path.name} 仍包含未替换模板变量")


def validate_html_output_file(
    path: Path, required_terms: list[str], errors: list[str]
) -> None:
    if not path.is_file():
        errors.append(f"缺少最终文档: {path}")
        return
    text = path.read_text(encoding="utf-8-sig")
    lowered = text.lower()
    if "<html" not in lowered or "<body" not in lowered:
        errors.append(f"{path.name} 不是完整 HTML 文档")
    for term in required_terms:
        if term not in text:
            errors.append(f"{path.name} 缺少必要内容: {term}")
    if "{{" in text or "}}" in text:
        errors.append(f"{path.name} 仍包含未替换模板变量")


def validate(
    trace_dir: Path, output_target: Path
) -> tuple[list[str], list[str]]:
    """Validate artifacts.

    `output_target` should be ProjectOutputDir. For compatibility, passing a
    `review_analysis.md` path validates only the legacy review document.
    """

    errors: list[str] = []
    warnings: list[str] = []
    legacy_review_only = output_target.suffix.lower() == ".md"
    output_dir = output_target.parent if legacy_review_only else output_target

    plan = load_json(trace_dir / "plan.json", errors)
    planned_agents: set[str] = set()
    if isinstance(plan, dict):
        require_fields(
            plan,
            {"level", "rationale", "confidence", "trace_id", "stages"},
            "plan.json",
            errors,
        )
        if not isinstance(plan.get("stages"), list):
            errors.append("plan.json: stages 必须是数组")
        else:
            for stage_index, stage in enumerate(plan["stages"], start=1):
                if not isinstance(stage, dict) or not isinstance(stage.get("tasks"), list):
                    errors.append(f"plan.json: stage {stage_index} 缺少 tasks 数组")
                    continue
                for task in stage["tasks"]:
                    task_fields = {
                        "task_id",
                        "agent",
                        "intent",
                        "params",
                        "context_hint",
                        "read_only",
                        "depends_on",
                    }
                    if not require_fields(
                        task, task_fields, f"plan.json/stage[{stage_index}]", errors
                    ):
                        continue
                    agent = str(task["agent"]).strip()
                    if agent:
                        planned_agents.add(agent)
                    if task["read_only"] is False and agent != "global_summary_tpm":
                        errors.append(f"plan.json: 非汇总 Agent 不得写入: {agent}")

    results_dir = trace_dir / "agent_results"
    result_agents: set[str] = set()
    all_result_risks: list[dict[str, Any]] = []
    per_result_ids: set[str] = set()
    if not results_dir.is_dir():
        errors.append(f"缺少 Agent 结果目录: {results_dir}")
    else:
        for result_path in sorted(results_dir.glob("*.json")):
            result = load_json(result_path, errors)
            fields = {
                "schema_version",
                "task_id",
                "agent",
                "domain",
                "status",
                "summary",
                "risks",
                "open_questions",
                "handoffs",
                "warnings",
            }
            if not require_fields(result, fields, result_path.name, errors):
                continue
            result_agents.add(str(result["agent"]).strip())
            if result["status"] not in ALLOWED_AGENT_STATUSES:
                errors.append(f"{result_path.name}: 非法 Agent 状态 {result['status']}")
            if not isinstance(result["risks"], list):
                errors.append(f"{result_path.name}: risks 必须是数组")
                continue
            for index, risk in enumerate(result["risks"], start=1):
                validate_risk(
                    risk,
                    f"{result_path.name}/risks[{index}]",
                    errors,
                    per_result_ids,
                )
                if isinstance(risk, dict):
                    all_result_risks.append(risk)

    special_agents = {
        "risk_review_planner",
        "evidence_critic_tpm",
        "global_summary_tpm",
        *DECISION_AGENTS,
    }
    domain_agents = {agent for agent in planned_agents if agent not in special_agents}
    missing_results = sorted(domain_agents - result_agents)
    if missing_results:
        warnings.append(f"计划中的领域 Agent 未产出结果: {', '.join(missing_results)}")

    critic = load_json(trace_dir / "critic_result.json", errors)
    if isinstance(critic, dict):
        require_fields(
            critic,
            {
                "schema_version",
                "agent",
                "status",
                "unsupported_risks",
                "conditional_inference_misuse",
                "duplicate_groups",
                "fact_conflicts",
                "severity_conflicts",
                "boundary_violations",
                "missing_agents",
                "recommendations",
            },
            "critic_result.json",
            errors,
        )

    decision_dir = trace_dir / "decision_results"
    version_data = load_json(decision_dir / "version_fit_tpm.json", errors)
    nonstandard_data = load_json(
        decision_dir / "nonstandard_classifier_tpm.json", errors
    )
    effort_data = load_json(decision_dir / "effort_estimation_tpm.json", errors)
    validate_version_result(version_data, "version_fit_tpm.json", errors)
    delivery_ids = validate_nonstandard_result(
        nonstandard_data, "nonstandard_classifier_tpm.json", errors
    )
    validate_effort_result(
        effort_data,
        "effort_estimation_tpm.json",
        delivery_ids,
        errors,
    )

    final_register = load_json(trace_dir / "final_risk_register.json", errors)
    final_risks: list[Any] = []
    if isinstance(final_register, list):
        final_risks = final_register
    elif isinstance(final_register, dict):
        candidate = final_register.get("risks")
        if not isinstance(candidate, list):
            errors.append("final_risk_register.json 必须是数组或包含 risks 数组")
        else:
            final_risks = candidate
    final_ids: set[str] = set()
    for index, risk in enumerate(final_risks, start=1):
        validate_risk(
            risk,
            f"final_risk_register.json/risks[{index}]",
            errors,
            final_ids,
        )

    manifest = load_json(trace_dir / "final_manifest.json", errors)
    if isinstance(manifest, dict):
        fields = {
            "schema_version",
            "project_key",
            "trace_id",
            "execution_mode",
            "completed_agents",
            "failed_agents",
            "not_applicable_agents",
            "decision_agents",
            "conflict_count",
            "current_risk_count",
            "pending_confirmation_count",
            "scope_change_warning_count",
            "overall_risk_level",
            "output_files",
            "approval_status",
        }
        if require_fields(manifest, fields, "final_manifest.json", errors):
            if not isinstance(manifest["decision_agents"], dict):
                errors.append("final_manifest.json: decision_agents 必须是对象")
            else:
                missing_decision_agents = sorted(
                    DECISION_AGENTS - set(manifest["decision_agents"])
                )
                if missing_decision_agents:
                    errors.append(
                        "final_manifest.json: decision_agents 缺少 "
                        + ", ".join(missing_decision_agents)
                    )
            expected_outputs = set(OUTPUT_SPECS) | set(HTML_OUTPUT_SPECS)
            if not isinstance(manifest["output_files"], list):
                errors.append("final_manifest.json: output_files 必须是数组")
            else:
                missing_outputs = sorted(
                    expected_outputs - set(manifest["output_files"])
                )
                if missing_outputs:
                    errors.append(
                        "final_manifest.json: output_files 缺少 "
                        + ", ".join(missing_outputs)
                    )
            if not isinstance(manifest["approval_status"], dict):
                errors.append("final_manifest.json: approval_status 必须是对象")
            else:
                missing_approvals = sorted(
                    {"version", "nonstandard", "effort"}
                    - set(manifest["approval_status"])
                )
                if missing_approvals:
                    errors.append(
                        "final_manifest.json: approval_status 缺少 "
                        + ", ".join(missing_approvals)
                    )

    specs = (
        {"review_analysis.md": OUTPUT_SPECS["review_analysis.md"]}
        if legacy_review_only
        else OUTPUT_SPECS
    )
    for filename, spec in specs.items():
        path = output_target if legacy_review_only else output_dir / filename
        validate_output_file(path, spec, errors)
    if not legacy_review_only:
        for filename, required_terms in HTML_OUTPUT_SPECS.items():
            validate_html_output_file(
                output_dir / filename, required_terms, errors
            )

    if not all_result_risks:
        warnings.append("所有领域 Agent 均未报告风险；请确认是确实无风险还是输入不足")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验多 Agent 风险评审与交付决策产物")
    parser.add_argument("--trace-dir", required=True, type=Path)
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--output-dir", type=Path)
    target_group.add_argument(
        "--review-file",
        type=Path,
        help="兼容旧流程：只校验 review_analysis.md；新流程请使用 --output-dir",
    )
    args = parser.parse_args()

    target = args.output_dir or args.review_file
    assert target is not None
    errors, warnings = validate(args.trace_dir.resolve(), target.resolve())
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")
    if errors:
        print(f"校验失败: {len(errors)} 个错误, {len(warnings)} 个警告")
        return 1
    print(f"校验通过: 0 个错误, {len(warnings)} 个警告")
    return 0


if __name__ == "__main__":
    sys.exit(main())
