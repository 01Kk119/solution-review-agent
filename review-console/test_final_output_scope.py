from pathlib import Path


def test_final_output_only_includes_latest_formal_deliverables():
    app_js = (Path(__file__).parent / "static" / "app.js").read_text(encoding="utf-8")
    assert "selectLatestFinalOutputs(state.selected.artifacts,state.selected.runs)" in app_js
    assert "Number(a.stage_index)===6" in app_js
    assert "Number(a.is_final)===1" in app_js
    assert "Number(a.stage_index)===5||Number(a.is_final)===1" not in app_js
    for artifact_type in (
        "方案评审主报告",
        "版本适配建议",
        "定制化开发清单",
        "非标判定清单",
        "人时估算清单",
    ):
        assert f'"{artifact_type}"' in app_js
    assert "latestRunId=runs.map(r=>r.id).find" in app_js
    assert '"主报告":"正式附件"' in app_js
