import app


def test_recommended_version_card_only_returns_conclusion():
    raw = (
        "# 版本适配建议\n\n"
        "项目统一版本：5.3.2\n"
        "版本风险等级：中\n"
        "5.2.2满足全部需求：否\n"
        "5.3.2满足全部需求：是\n\n"
        "## 模块能力证据\n\n大量明细"
    )
    assert (
        app._extract_decision_card_content("recommended_version", raw)
        == "5.3.2（中风险）"
    )


def test_other_cards_only_return_named_local_section():
    risk = "# 主报告\n\n## 5. 关键风险\n\n| ID | 风险 |\n|---|---|\n| R1 | 示例 |\n\n## 6. 待确认事项\n\n其他"
    custom = "# 清单\n\n## 已确认定制/非标开发\n\n无\n\n## 标准能力\n\n大量明细"
    effort = "# 人时\n\n### 工作项人时表\n\n大量明细\n\n### 汇总\n\n总计：40人时\n\n### 假设\n\n其他"
    assert "待确认事项" not in app._extract_decision_card_content("risk_items", risk)
    assert app._extract_decision_card_content("custom_development", custom) == "无"
    assert (
        app._extract_decision_card_content("effort_estimation", effort)
        == "总计：40人时"
    )
