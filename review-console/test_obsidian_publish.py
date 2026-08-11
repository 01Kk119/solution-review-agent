from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import app


class ObsidianPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.original_vault = app.OBSIDIAN_VAULT_DIR
        self.original_enabled = app.OBSIDIAN_PUBLISH_ENABLED
        app.OBSIDIAN_VAULT_DIR = Path(self.temporary.name)
        app.OBSIDIAN_PUBLISH_ENABLED = True
        self.project = {
            "id": "project-id",
            "project_key": "vn99999",
            "name": "VN99999,测试项目",
        }

    def tearDown(self):
        app.OBSIDIAN_VAULT_DIR = self.original_vault
        app.OBSIDIAN_PUBLISH_ENABLED = self.original_enabled
        self.temporary.cleanup()

    def test_publishes_all_stages_and_archives_previous_final(self):
        stages = [
            (2, "requirements_model.md", "需求模型", "# 需求模型"),
            (3, "domain_review.md", "AI领域评审", "# 专业评审"),
            (4, "evidence_critique.md", "AI证据质检", "# 证据质检"),
            (5, "delivery_decisions.md", "AI交付决策", "# 交付决策"),
            (6, "final_review.md", "AI最终评审结果", "# 最终报告 v1"),
        ]
        for stage_index, filename, artifact_type, content in stages:
            result = app.publish_ai_artifact_to_obsidian(
                self.project, "run-1", stage_index, filename, artifact_type, content
            )
            self.assertIsNotNone(result)
            self.assertTrue(result.exists())

        project_dir = app.OBSIDIAN_VAULT_DIR / "review_outputs" / "vn99999"
        final_reports = list(
            (project_dir / "final").glob("vn99999_final_review_????????_v001.md")
        )
        self.assertEqual(len(final_reports), 1)
        final_report = final_reports[0]
        self.assertEqual(final_report.read_text(encoding="utf-8"), "# 最终报告 v1")

        app.publish_ai_artifact_to_obsidian(
            self.project,
            "run-2",
            6,
            "final_review.md",
            "AI最终评审结果",
            "# 最终报告 v2",
        )
        self.assertEqual(final_report.read_text(encoding="utf-8"), "# 最终报告 v2")
        archived = list(
            (project_dir / "final" / "history").rglob(
                "vn99999_final_review_????????_v001.md"
            )
        )
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].read_text(encoding="utf-8"), "# 最终报告 v1")

        project_index = (project_dir / "project_output_index.md").read_text(encoding="utf-8")
        self.assertIn("## 唯一最终结果", project_index)
        self.assertIn(final_report.stem, project_index)

        review_index = (
            app.OBSIDIAN_VAULT_DIR / "review_outputs" / "review_index.md"
        ).read_text(encoding="utf-8")
        entry = (
            "- [[review_outputs/vn99999/project_output_index|"
            "vn99999]]"
        )
        self.assertEqual(review_index.count(entry), 1)
        generated_paths = [
            path.relative_to(app.OBSIDIAN_VAULT_DIR)
            for path in app.OBSIDIAN_VAULT_DIR.rglob("*")
        ]
        self.assertTrue(all(str(path).isascii() for path in generated_paths))

    def test_non_ascii_project_key_uses_stable_ascii_fallback(self):
        project = {
            "id": "project-without-number",
            "project_key": "无项目号",
            "name": "中文项目名称",
        }
        target = app.publish_ai_artifact_to_obsidian(
            project,
            "run-1",
            6,
            "final_review.md",
            "AI最终评审结果",
            "# Final",
        )
        self.assertIsNotNone(target)
        self.assertTrue(str(target.relative_to(app.OBSIDIAN_VAULT_DIR)).isascii())
        self.assertRegex(
            target.name,
            r"^project_[a-f0-9]{10}_final_review_\d{8}_v001\.md$",
        )


if __name__ == "__main__":
    unittest.main()
