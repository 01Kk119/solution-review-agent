import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).parent / "app.py"
SPEC = importlib.util.spec_from_file_location("review_console_app_version_test", APP_PATH)
APP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(APP)


def test_scenario_context_routes_domains_and_expands_software_keywords():
    requirements = (
        "REQ-001：白木托盘从高位货架取货，叉口净空88.9mm。\n"
        "REQ-002：窄巷道导航宽度3250mm，要求定位精度±10mm。\n"
        "REQ-003：WMS下发任务，PLC控制自动门，完成后状态回传。"
    )
    context = APP.build_version_scenario_context(requirements, "")
    assert "## 取放场景卡" in context
    assert "## 导航场景卡" in context
    assert "## 软件能力检索卡" in context
    assert "WMS API" in context
    assert "PLC接口" in context
    assert "门控联动" in context
    assert "状态回传" in context


def test_522_pass_stops_532_probe():
    raw = (
        "项目统一版本：5.3.2\n版本风险等级：中\n"
        "5.2.2满足全部需求：是（规格表已覆盖）\n"
        "5.3.2满足全部需求：是\n版本上探5.3.2：是\n\n## 证据\n- CAP-01"
    )
    normalized = APP.normalize_unified_version_decision(raw)
    assert "项目统一版本：5.2.2" in normalized
    assert "版本风险等级：低" in normalized
    assert "5.3.2满足全部需求：未评估" in normalized
    assert "版本上探5.3.2：否" in normalized
    APP.validate_unified_version_decision(normalized)


def test_522_fail_532_pass_selects_532_and_keeps_gap_body():
    raw = (
        "项目统一版本：待确认\n版本风险等级：待确认\n"
        "5.2.2满足全部需求：否\n5.3.2满足全部需求：是\n"
        "版本上探5.3.2：是\n\n## 5.2.2差距\n- 高位货架闭环不支持"
    )
    normalized = APP.normalize_unified_version_decision(raw)
    assert "项目统一版本：5.3.2" in normalized
    assert "版本风险等级：中" in normalized
    assert "高位货架闭环不支持" in normalized
    APP.validate_unified_version_decision(normalized)


def test_both_versions_fail_selects_none_and_keeps_separate_gaps():
    raw = (
        "5.2.2满足全部需求：否\n5.3.2满足全部需求：否\n"
        "## 5.2.2差距\n- 不支持横梁式货架闭环\n"
        "## 5.3.2差距\n- 仍不支持横梁式货架闭环"
    )
    normalized = APP.normalize_unified_version_decision(raw)
    assert "项目统一版本：暂无标准版本可满足" in normalized
    assert "版本风险等级：高" in normalized
    assert "## 5.2.2差距" in normalized
    assert "## 5.3.2差距" in normalized
    APP.validate_unified_version_decision(normalized)


def test_pending_wording_is_normalized_without_aborting_review():
    raw = (
        "项目统一版本：5.2.2\n版本风险等级：中\n"
        "5.2.2满足全部需求：否\n"
        "5.3.2满足全部需求：待版本负责人确认（缺少权威基线）\n"
        "版本上探5.3.2：否"
    )
    normalized = APP.normalize_unified_version_decision(raw)
    assert "项目统一版本：待确认" in normalized
    assert "版本风险等级：待确认" in normalized
    assert "5.3.2满足全部需求：待确认" in normalized
    APP.validate_unified_version_decision(normalized)
