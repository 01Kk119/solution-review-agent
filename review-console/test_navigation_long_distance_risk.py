import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).parent / "app.py"
SPEC = importlib.util.spec_from_file_location("review_console_app_navigation_test", APP_PATH)
APP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(APP)


def test_navigation_retrieval_terms_cover_long_repetitive_scenes():
    terms = APP.ROLE_RETRIEVAL_TERMS["navigation"]
    for expected in ("线库", "货架", "车厢", "累计漂移"):
        assert expected in terms


def test_navigation_knowledge_contains_long_distance_high_risk_rule():
    content = APP.load_role_knowledge("navigation")
    assert "长距离累计漂移专项规则" in content
    assert "连续导航长度大于15 m" in content
    assert "缺少以上证据时保持高风险" in content
