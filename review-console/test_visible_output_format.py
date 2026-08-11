from pathlib import Path


def test_visible_output_preambles_are_removed():
    app_py = (Path(__file__).parent / "app.py").read_text(encoding="utf-8")
    assert "def strip_agent_preamble(content: str) -> str:" in app_py
    assert "result.content = strip_agent_preamble(result.content)" in app_py
    assert "content = strip_agent_preamble(content)" in app_py
    assert 'f"{strip_agent_preamble(body)' in app_py
    assert "只输出最终结果，直接从标题、表头或第一条结论开始" in app_py
    assert "global_summary:v6" in app_py
    assert "decision:{slug}:v5" in app_py


def test_runner_process_banner_is_not_written_to_attachments():
    app_py = (Path(__file__).parent / "app.py").read_text(encoding="utf-8")
    assert "本附件由 Runner" not in app_py


def test_known_agent_openings_are_removed():
    import app

    version = (
        "好的，作为版本适配 Agent，我已根据 5.3.2 条件索引，对 5.2.2 初步版本结论"
        "进行缺口比对，并输出修订后的完整版本结论。\n\n# 版本适配建议\n\n结论"
    )
    summary = (
        "好的，作为 Global Summary TPM，我已根据所有上游专业结论、风险汇总、证据质检、"
        "版本适配、非标判定和人时估算结果，生成最终方案评审主报告。\n\n"
        "# 方案评审主报告\n\n结论"
    )
    assert app.strip_agent_preamble(version).startswith("# 版本适配建议")
    assert app.strip_agent_preamble(summary).startswith("# 方案评审主报告")
