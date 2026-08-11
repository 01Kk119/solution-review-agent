from pathlib import Path


def test_global_summary_uses_fixed_concise_structure():
    app_py = (Path(__file__).parent / "app.py").read_text(encoding="utf-8")
    assert "global_summary:v5" in app_py
    assert "从“# 方案评审主报告”直接开始" in app_py
    assert "章节名称、顺序和表头不得增删、合并或改名" in app_py
    assert "寒暄、角色自述、任务复述、过程说明、完成宣告或文件清单" in app_py
    assert "表达尽量口语化" in app_py
    assert "避免公文式套话" in app_py
    assert "不得因口语化弱化风险等级" in app_py
    for section in (
        "1.评审结论",
        "2.项目概览",
        "3.分领域结论",
        "4.交付决策摘要",
        "5.关键风险",
        "6.待确认事项",
        "7.下一步动作",
    ):
        assert section in app_py


def test_skill_template_has_only_fixed_result_sections():
    template = (
        Path(__file__).parents[1]
        / "Agent工作区"
        / "skills"
        / "global-summary-tpm"
        / "assets"
        / "review_analysis_template.md"
    ).read_text(encoding="utf-8")
    assert template.startswith("# 方案评审主报告\n")
    assert [line for line in template.splitlines() if line.startswith("## ")] == [
        "## 1. 评审结论",
        "## 2. 项目概览",
        "## 3. 分领域结论",
        "## 4. 交付决策摘要",
        "## 5. 关键风险",
        "## 6. 待确认事项",
        "## 7. 下一步动作",
    ]
