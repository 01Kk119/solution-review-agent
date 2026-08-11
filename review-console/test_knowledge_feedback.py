import gc
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

import app


class FakeDeepSeekClient:
    configured = True
    model = "fake-deepseek"

    def __init__(self, content: str):
        self.content = content

    def chat(self, messages, **kwargs):
        return SimpleNamespace(
            content=self.content,
            model=self.model,
            trace_id="trace-feedback",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )


class FailingDeepSeekClient:
    configured = True

    def chat(self, messages, **kwargs):
        raise app.DeepSeekError("temporary failure")


class KnowledgeFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.originals = {
            name: getattr(app, name)
            for name in (
                "DATA_DIR",
                "UPLOAD_DIR",
                "GENERATED_DIR",
                "UPLOAD_CHUNK_DIR",
                "DB_PATH",
                "SOURCE_PROJECTS",
                "OBSIDIAN_VAULT_DIR",
                "KNOWLEDGE_BASE_DIR",
            )
        }
        app.DATA_DIR = self.root / "data"
        app.UPLOAD_DIR = app.DATA_DIR / "uploads"
        app.GENERATED_DIR = app.DATA_DIR / "generated"
        app.UPLOAD_CHUNK_DIR = app.DATA_DIR / "upload_chunks"
        app.DB_PATH = app.DATA_DIR / "review_console.db"
        app.SOURCE_PROJECTS = self.root / "empty-source-projects"
        app.OBSIDIAN_VAULT_DIR = self.root / "vault"
        app.KNOWLEDGE_BASE_DIR = app.OBSIDIAN_VAULT_DIR / "agent" / "03_knowledge"
        self.target = (
            app.KNOWLEDGE_BASE_DIR
            / app.FEEDBACK_KNOWLEDGE_TARGETS["pick_place"]["relative_path"]
        )
        self.target.parent.mkdir(parents=True)
        self.target.write_text(
            "# 取放开发风险索引\n\n## 当前规则\n\n- 标准能力基线。\n",
            encoding="utf-8",
        )
        app.init_db()
        self.project_id = "project-feedback"
        self.project_dir = app.UPLOAD_DIR / "vn26001"
        self.project_dir.mkdir(parents=True)
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO projects(
                  id, project_key, name, source_path, created_at, updated_at
                )
                VALUES(?,?,?,?,?,?)
                """,
                (
                    self.project_id,
                    "vn26001",
                    "Feedback Test",
                    str(self.project_dir),
                    stamp,
                    stamp,
                ),
            )

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(app, name, value)
        gc.collect()
        self.temporary.cleanup()

    def payload(self):
        return {
            "title": "放货容差计算补充",
            "source_type": "计算结果",
            "target_key": "pick_place",
            "version_info": "5.2.2",
            "vehicle_info": "VNE40 + 料车",
            "scenario": "料车存在动态停靠角度时放货",
            "exclusions": "无反光板时不适用",
            "raw_content": "TPM 复核后确认应按角度误差和货叉侧隙共同计算。",
            "attachment_ids": [],
            "calculation": {
                "parameters": "角度误差、货叉侧隙",
                "measured_value": "20",
                "unit": "mm",
                "data_source": "现场测量",
                "method": "几何叠加",
                "formula": "A+B",
                "result": "30mm",
                "threshold": "40mm",
                "conclusion": "当前能力可满足",
            },
        }

    def patch_analysis(self):
        return """
# KB-FB-0001 AI 知识分析

## 1. 分析结论

- 判定：可新增

## 4. 建议加入知识库的内容

<!-- KB_PATCH_START -->
### KB-FB-0001 动态角度放货容差

- 知识类型：新增
- 适用条件：料车停靠角度会动态变化
- 风险判定规则：计算结果超过允许侧隙时标为开发风险
- 证据/计算依据：TPM 计算记录
- 待确认项：现场复测
<!-- KB_PATCH_END -->
""".strip()

    def test_create_analyze_edit_and_publish_with_history(self):
        item = app.create_knowledge_feedback(self.project_id, self.payload())
        self.assertEqual(item["status"], "待分析")
        self.assertTrue(Path(item["raw_md_path"]).is_file())
        self.assertIn("TPM 原始反馈", item["raw_markdown"])
        self.assertNotIn(str(Path(item["raw_md_path"])), [row["stored_path"] for row in app.project_payload(self.project_id)["files"]])

        item = app.analyze_knowledge_feedback(
            item["id"], FakeDeepSeekClient(self.patch_analysis())
        )
        self.assertEqual(item["status"], "待确认")
        self.assertTrue(Path(item["analysis_md_path"]).is_file())
        with self.assertRaises(RuntimeError):
            app.update_knowledge_feedback_raw(item["id"], self.payload())

        edited = item["analysis_content"].replace("现场复测", "项目现场复测")
        item = app.update_knowledge_feedback_analysis(item["id"], edited)
        self.assertIn("项目现场复测", item["analysis_content"])

        item = app.publish_knowledge_feedback(item["id"], confirmed=True)
        self.assertEqual(item["status"], "已发布")
        target_content = self.target.read_text(encoding="utf-8")
        self.assertIn("## TPM 已确认反馈（优先规则）", target_content)
        self.assertEqual(target_content.count("### KB-FB-0001"), 1)
        self.assertTrue(Path(item["backup_path"]).is_file())
        self.assertTrue(Path(item["confirmed_md_path"]).is_file())

        item = app.publish_knowledge_feedback(item["id"], confirmed=True)
        self.assertEqual(item["status"], "已发布")
        self.assertEqual(
            self.target.read_text(encoding="utf-8").count("### KB-FB-0001"), 1
        )

    def test_publish_rejects_changed_knowledge_base(self):
        item = app.create_knowledge_feedback(self.project_id, self.payload())
        item = app.analyze_knowledge_feedback(
            item["id"], FakeDeepSeekClient(self.patch_analysis())
        )
        self.target.write_text(
            self.target.read_text(encoding="utf-8") + "\n- 他人新增规则\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(RuntimeError, "重新执行 AI 分析"):
            app.publish_knowledge_feedback(item["id"], confirmed=True)
        self.assertNotIn(
            "### KB-FB-0001", self.target.read_text(encoding="utf-8")
        )

    def test_confirm_no_change_archives_without_modifying_knowledge(self):
        item = app.create_knowledge_feedback(self.project_id, self.payload())
        before = self.target.read_text(encoding="utf-8")
        no_change = """
# KB-FB-0001 AI 知识分析

## 1. 分析结论

- 判定：无需修改

## 4. 建议加入知识库的内容

<!-- KB_PATCH_START -->
无需写入知识库。
<!-- KB_PATCH_END -->
""".strip()
        item = app.analyze_knowledge_feedback(
            item["id"], FakeDeepSeekClient(no_change)
        )
        item = app.publish_knowledge_feedback(item["id"], confirmed=True)
        self.assertEqual(item["status"], "已归档")
        self.assertEqual(self.target.read_text(encoding="utf-8"), before)
        self.assertTrue(Path(item["confirmed_md_path"]).is_file())

    def test_publish_requires_human_confirmation(self):
        item = app.create_knowledge_feedback(self.project_id, self.payload())
        item = app.analyze_knowledge_feedback(
            item["id"], FakeDeepSeekClient(self.patch_analysis())
        )
        with self.assertRaises(PermissionError):
            app.publish_knowledge_feedback(item["id"], confirmed=False)

    def test_failed_reanalysis_keeps_previous_confirmable_result(self):
        item = app.create_knowledge_feedback(self.project_id, self.payload())
        item = app.analyze_knowledge_feedback(
            item["id"], FakeDeepSeekClient(self.patch_analysis())
        )
        previous_analysis = item["analysis_content"]
        with self.assertRaises(app.DeepSeekError):
            app.analyze_knowledge_feedback(item["id"], FailingDeepSeekClient())
        item = app._feedback_payload(
            app._feedback_row(item["id"]), include_content=True
        )
        self.assertEqual(item["status"], "待确认")
        self.assertTrue(item["can_publish"])
        self.assertEqual(item["analysis_content"], previous_analysis)


if __name__ == "__main__":
    unittest.main()
