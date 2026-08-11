import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).parent / "app.py"
SPEC = importlib.util.spec_from_file_location("review_console_app_pick_place_test", APP_PATH)
APP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(APP)


def test_cross_project_filename_is_isolated():
    assert APP.is_cross_project_filename("VN26076", "VN26064项目需求细化.md")
    assert not APP.is_cross_project_filename("VN26076", "VN26076技术协议.pdf")
    assert not APP.is_cross_project_filename("VN26076", "北美方案评审周会.md")


def test_pick_place_coverage_requires_all_three_26076_risks():
    evidence = (
        "Bay B顶部没有凸出来的立柱特征，至少保证300毫米检测高度，计划与客户商议改造。\n"
        "最大举升高度9455mm，左右总间隙406mm，由三处间隙组成。\n"
        "72英寸托盘最大叉距710mm，垂直间隙90mm，左右最小间隙20mm，客户同意修改中间块。"
    )
    gaps = APP.pick_place_review_coverage_gaps(evidence, "当前资料需要确认。")
    assert len(gaps) == 3


def test_pick_place_coverage_accepts_explicit_unclosed_high_risks():
    evidence = (
        "Bay B顶部没有凸出来的立柱特征，至少保证300毫米检测高度。\n"
        "最大举升高度9455mm，左右总间隙406mm，由三处间隙组成。\n"
        "最大叉距710mm，垂直间隙90mm，左右最小间隙20mm。"
    )
    review = (
        "| PP-R01 | 高 | Bay B顶部无立柱，要求300mm，当前不满足；改造未关闭 |\n"
        "| PP-R02 | 高 | 举升9455mm，406mm为三处总间隙，高位放货不满足 |\n"
        "| PP-R03 | 高 | 叉距710mm，垂直90mm、横向20mm容差偏紧，改造未关闭 |"
    )
    assert APP.pick_place_review_coverage_gaps(evidence, review) == []


def test_live_26076_pick_place_evidence_recalls_meeting_facts_when_available():
    project_id = "370e508b-f694-4522-8a05-6ea18127ef71"
    evidence = APP.load_domain_project_evidence(project_id, "pick_place")
    if not evidence:
        return
    assert "300" in evidence
    assert "立柱" in evidence
    assert "406" in evidence
    assert "90" in evidence
    assert "20" in evidence
    assert "VN26064项目需求细化.md" not in evidence
