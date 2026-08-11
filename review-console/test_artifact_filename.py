import app


def test_local_artifact_filename_puts_stage_first():
    app_py = open(app.__file__, encoding="utf-8").read()
    assert (
        'f"{stage_index + 1:02d}_{project_slug}_{artifact_slug}_{date_code}_'
        'v{version:03d}{extension}"'
    ) in app_py
    assert 'f"00_{project_slug}_file_catalog_{date_code}.md"' in app_py


def test_obsidian_artifact_filename_puts_stage_first():
    name = app._obsidian_artifact_name(
        "0727",
        6,
        "version_recommendation.md",
        "版本适配建议",
        "20260729",
        1,
    )
    assert name == "07_0727_version_recommendation_20260729_v001.md"
