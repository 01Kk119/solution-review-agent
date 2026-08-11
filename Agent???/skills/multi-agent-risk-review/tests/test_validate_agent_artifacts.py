from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_agent_artifacts.py"
SPEC = importlib.util.spec_from_file_location("validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def valid_risk() -> dict:
    return {
        "risk_id": "MM-001",
        "domain": "mingmou",
        "title": "视野参数待确认",
        "statement": "项目要求与已知测试边界需要实测确认。",
        "status": "pending_confirmation",
        "severity": "中",
        "basis_type": "AI推断待确认",
        "evidence_refs": ["E001"],
        "impact": "可能影响相机覆盖。",
        "recommendation": "设计冻结前完成仿真与实测。",
        "owner": "算法/方案",
        "confidence": 0.8,
        "handoff_to": ["software_rcs_interface_tpm"],
    }


def output_text(spec: dict[str, list[str]]) -> str:
    parts = ["# 测试项目"]
    parts.extend(spec["headings"])
    parts.extend(spec["headers"])
    return "\n\n".join(parts) + "\n"


def html_output_text(required_terms: list[str]) -> str:
    return (
        "<!doctype html><html><body>"
        + " ".join(required_terms)
        + "</body></html>"
    )


class ValidatorTests(unittest.TestCase):
    def build_valid_fixture(self, root: Path) -> tuple[Path, Path]:
        trace = root / "trace"
        decision_tasks = [
            {
                "task_id": f"t-{agent}",
                "agent": agent,
                "intent": "decision",
                "params": {},
                "context_hint": {},
                "read_only": True,
                "depends_on": ["t-critic"],
            }
            for agent in sorted(validator.DECISION_AGENTS)
        ]
        write_json(
            trace / "plan.json",
            {
                "level": "L3",
                "rationale": "test",
                "confidence": 0.9,
                "trace_id": "trace-test",
                "stages": [
                    {
                        "name": "domain_review",
                        "tasks": [
                            {
                                "task_id": "t-mm",
                                "agent": "mingmou_risk_tpm",
                                "intent": "review",
                                "params": {},
                                "context_hint": {},
                                "read_only": True,
                                "depends_on": [],
                            }
                        ],
                    },
                    {"name": "delivery_decision", "tasks": decision_tasks},
                    {
                        "name": "synthesis",
                        "tasks": [
                            {
                                "task_id": "t-summary",
                                "agent": "global_summary_tpm",
                                "intent": "write outputs",
                                "params": {},
                                "context_hint": {},
                                "read_only": False,
                                "depends_on": [task["task_id"] for task in decision_tasks],
                            }
                        ],
                    },
                ],
            },
        )
        write_json(
            trace / "agent_results" / "mingmou_risk_tpm.json",
            {
                "schema_version": "2.1",
                "task_id": "t-mm",
                "agent": "mingmou_risk_tpm",
                "domain": "mingmou",
                "status": "completed",
                "summary": "one risk",
                "risks": [valid_risk()],
                "open_questions": [],
                "handoffs": [],
                "warnings": [],
                "tool_calls_made": [],
                "tokens_used": 0,
            },
        )
        write_json(
            trace / "critic_result.json",
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
                "recommendations": [],
            },
        )

        decision_dir = trace / "decision_results"
        write_json(
            decision_dir / "version_fit_tpm.json",
            {
                "schema_version": "2.1",
                "agent": "version_fit_tpm",
                "status": "completed",
                "baseline_status": "available",
                "system_recommendations": [
                    {
                        "system": "vehicle",
                        "status": "applicable",
                        "release_type": "年度版本",
                        "factory_version": "V1",
                        "onsite_target_version": "V2",
                        "recommendation_type": "upgrade_onsite",
                        "capability_reason": "支持测试能力",
                        "dependencies": [],
                        "validation_plan": "到场测试",
                        "rollback_plan": "保留 V1",
                        "evidence_refs": ["E001", "VER-001"],
                        "confidence": 0.8,
                    }
                ],
                "alternatives": [],
                "capability_matches": [],
                "gaps": [],
                "assumptions": [],
                "approval_required_by": ["版本负责人"],
                "confidence": 0.8,
            },
        )
        write_json(
            decision_dir / "nonstandard_classifier_tpm.json",
            {
                "schema_version": "2.1",
                "agent": "nonstandard_classifier_tpm",
                "status": "completed",
                "baseline_status": "available",
                "items": [
                    {
                        "item_id": "DEL-001",
                        "title": "状态映射",
                        "module": "RCS",
                        "classification": "nonstandard_development",
                        "requirement_refs": ["REQ-001"],
                        "risk_refs": ["MM-001"],
                        "evidence_refs": ["E001"],
                        "implementation_method": "新增状态映射",
                        "standard_boundary": "V1 不支持",
                        "justification": "需新增产品能力",
                        "deliverable": "接口实现",
                        "acceptance_criteria": "联调通过",
                        "close_condition": "异常恢复验证通过",
                        "dependencies": [],
                        "owner_role": "软件",
                        "version_strategy": "补丁版本",
                        "approval_required_by": ["版本负责人"],
                        "confidence": 0.75,
                    }
                ],
                "custom_development_item_ids": ["DEL-001"],
                "nonstandard_item_ids": ["DEL-001"],
                "pending_classification": [],
                "out_of_scope_item_ids": [],
                "warnings": [],
            },
        )
        write_json(
            decision_dir / "effort_estimation_tpm.json",
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
                        "title": "状态映射",
                        "estimate_status": "estimated",
                        "role_hours": [
                            {
                                "phase": "开发",
                                "role": "软件",
                                "low": 8,
                                "likely": 16,
                                "high": 24,
                            }
                        ],
                        "total_hours": {"low": 8, "likely": 16, "high": 24},
                        "estimate_basis": ["BASE-001"],
                        "assumptions": ["接口冻结"],
                        "exclusions": ["客户等待"],
                        "confidence": 0.7,
                    }
                ],
                "totals": {"low": 8, "likely": 16, "high": 24},
                "unestimated_items": [],
                "approval_required_by": ["研发负责人", "TPM"],
                "warnings": [],
            },
        )

        write_json(trace / "final_risk_register.json", {"risks": [valid_risk()]})
        write_json(
            trace / "final_manifest.json",
            {
                "schema_version": "2.1",
                "project_key": "test",
                "trace_id": "trace-test",
                "execution_mode": "multi_agent",
                "completed_agents": [
                    "mingmou_risk_tpm",
                    *sorted(validator.DECISION_AGENTS),
                ],
                "failed_agents": [],
                "not_applicable_agents": [],
                "decision_agents": {
                    agent: "completed" for agent in validator.DECISION_AGENTS
                },
                "conflict_count": 0,
                "current_risk_count": 0,
                "pending_confirmation_count": 1,
                "scope_change_warning_count": 0,
                "overall_risk_level": "中",
                "output_files": [
                    *validator.OUTPUT_SPECS,
                    *validator.HTML_OUTPUT_SPECS,
                ],
                "approval_status": {
                    "version": "pending_version_owner",
                    "nonstandard": "pending_engineering_owner",
                    "effort": "pending_tpm_and_engineering",
                },
            },
        )

        for filename, spec in validator.OUTPUT_SPECS.items():
            (root / filename).write_text(output_text(spec), encoding="utf-8")
        for filename, required_terms in validator.HTML_OUTPUT_SPECS.items():
            (root / filename).write_text(
                html_output_text(required_terms), encoding="utf-8"
            )
        return trace, root

    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertEqual([], errors)

    def test_conditional_inference_cannot_be_current_risk(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            result_path = trace / "agent_results" / "mingmou_risk_tpm.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["risks"][0]["basis_type"] = "条件性推断"
            result["risks"][0]["status"] = "current_risk"
            write_json(result_path, result)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(any("条件性推断" in error for error in errors))

    def test_missing_final_document_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            (output_dir / "effort_recommendation.md").unlink()
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(
                any("effort_recommendation.md" in error for error in errors)
            )

    def test_missing_version_baseline_cannot_recommend_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            version_path = trace / "decision_results" / "version_fit_tpm.json"
            version = json.loads(version_path.read_text(encoding="utf-8"))
            version["baseline_status"] = "missing"
            version["system_recommendations"][0]["factory_version"] = "V1"
            version["system_recommendations"][0]["onsite_target_version"] = "V2"
            write_json(version_path, version)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(any("不得给出具体推荐版本" in error for error in errors))

    def test_unified_version_risk_mapping_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            version_path = trace / "decision_results" / "version_fit_tpm.json"
            version = json.loads(version_path.read_text(encoding="utf-8"))
            version.update(
                {
                    "schema_version": "2.2",
                    "unified_version": "5.3.2",
                    "version_risk_level": "低",
                    "fit_5_2_2": "否",
                    "fit_5_3_2": "是",
                }
            )
            version["system_recommendations"][0]["onsite_target_version"] = "5.3.2"
            write_json(version_path, version)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(any("统一版本与风险等级映射错误" in error for error in errors))

    def test_module_target_must_match_unified_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            version_path = trace / "decision_results" / "version_fit_tpm.json"
            version = json.loads(version_path.read_text(encoding="utf-8"))
            version.update(
                {
                    "schema_version": "2.2",
                    "unified_version": "5.3.2",
                    "version_risk_level": "中",
                    "fit_5_2_2": "否",
                    "fit_5_3_2": "是",
                }
            )
            version["system_recommendations"][0]["onsite_target_version"] = "5.2.2"
            write_json(version_path, version)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(any("必须与项目统一版本一致" in error for error in errors))

    def test_out_of_scope_cannot_be_confirmed_as_nonstandard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            result_path = trace / "decision_results" / "nonstandard_classifier_tpm.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["items"][0]["classification"] = "out_of_scope"
            write_json(result_path, result)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(
                any("nonstandard_item_ids 引用了非非标项" in error for error in errors)
            )

    def test_effort_must_reference_existing_source_item(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace, output_dir = self.build_valid_fixture(Path(directory))
            effort_path = trace / "decision_results" / "effort_estimation_tpm.json"
            effort = json.loads(effort_path.read_text(encoding="utf-8"))
            effort["items"][0]["source_item_id"] = "DEL-MISSING"
            write_json(effort_path, effort)
            errors, _warnings = validator.validate(trace, output_dir)
            self.assertTrue(
                any("source_item_id 未指向有效来源工作项" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
