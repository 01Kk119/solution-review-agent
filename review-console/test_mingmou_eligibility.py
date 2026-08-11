import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).parent / "app.py"
SPEC = importlib.util.spec_from_file_location("review_console_app_mingmou_test", APP_PATH)
APP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(APP)


def test_not_mentioned_does_not_trigger():
    context = "| 字段 | 结论 |\n| 明眸 | 未提及 |"
    assert APP.mingmou_requirement_status(context) == APP.MINGMOU_EXCLUDED
    assert not APP.needs_mingmou_review(context)


def test_explicit_exclusion_does_not_trigger():
    assert not APP.needs_mingmou_review("本项目无明眸需求，不包含库位视觉。")


def test_generic_project_terms_do_not_trigger():
    context = "白木托盘由机器人搬运，通过WMS下发四种流程，库位尺寸待确认。"
    assert APP.mingmou_requirement_status(context) == APP.MINGMOU_NOT_MENTIONED
    assert not APP.needs_mingmou_review(context)


def test_explicit_mingmou_requirement_triggers():
    context = "REQ-021：需要部署6台明眸摄像头，用于库位视觉监控。"
    assert APP.mingmou_requirement_status(context) == APP.MINGMOU_CONFIRMED
    assert APP.needs_mingmou_review(context)


def test_label_without_decision_is_only_possible():
    assert APP.mingmou_requirement_status("## 明眸需求") == APP.MINGMOU_POSSIBLE
    assert not APP.needs_mingmou_review("## 明眸需求")


def test_compact_context_excludes_unrelated_project_facts():
    context = "\n".join(
        (
            "REQ-001：白木托盘尺寸为1200mm。",
            "来源：客户需求.xlsx",
            "REQ-021：需要部署6台明眸摄像头。",
            "来源：视觉需求.docx，第3页",
            "REQ-030：WMS下发任务。",
        )
    )
    compact = APP.compact_mingmou_requirement_context(context)
    assert "REQ-021" in compact
    assert "视觉需求.docx" in compact
    assert "REQ-030" not in compact
