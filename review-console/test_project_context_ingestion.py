import gc
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import app


class ProjectContextIngestionTests(unittest.TestCase):
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
                "OBSIDIAN_VAULT_DIR",
            )
        }
        app.DATA_DIR = self.root / "data"
        app.UPLOAD_DIR = app.DATA_DIR / "uploads"
        app.GENERATED_DIR = app.DATA_DIR / "generated"
        app.UPLOAD_CHUNK_DIR = app.DATA_DIR / "upload_chunks"
        app.DB_PATH = app.DATA_DIR / "review_console.db"
        app.OBSIDIAN_VAULT_DIR = self.root / "vault"
        app.init_db()

        self.project_id = "project-f"
        self.source_dir = app.UPLOAD_DIR / "f-customer"
        self.source_dir.mkdir(parents=True)
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO projects
                (id, project_key, name, customer, source_path, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    self.project_id,
                    "f-customer",
                    "F客户",
                    "F",
                    str(self.source_dir),
                    stamp,
                    stamp,
                ),
            )

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(app, name, value)
        gc.collect()
        self.temporary.cleanup()

    def add_file(self, path: Path, file_id: str) -> None:
        raw = path.read_bytes()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO files
                (id, project_id, kind, name, stored_path, mime_type, size, sha256, created_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    file_id,
                    self.project_id,
                    "原始资料",
                    path.name,
                    str(path),
                    "",
                    len(raw),
                    hashlib.sha256(raw).hexdigest(),
                    app.now(),
                ),
            )

    def test_uploaded_xlsx_is_extracted_into_agent_context(self):
        workbook = self.source_dir / "Application Form.xlsx"
        with zipfile.ZipFile(workbook, "w") as archive:
            archive.writestr(
                "xl/worksheets/sheet1.xml",
                """<?xml version="1.0" encoding="UTF-8"?>
                <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
                  <sheetData><row r="1"><c r="A1"><v>F-CUSTOMER-CARRIER-TOLERANCE-42MM</v></c></row></sheetData>
                </worksheet>""",
            )
        self.add_file(workbook, "file-xlsx")

        context = app.load_project_context(self.project_id)

        self.assertIn("已登记 1 份原始资料，成功提取 1 份", context)
        self.assertIn("Application Form.xlsx", context)
        self.assertIn("F-CUSTOMER-CARRIER-TOLERANCE-42MM", context)
        self.assertNotIn("未接收到任何原始输入材料", context)

    def test_unparsed_attachment_is_reported_as_received(self):
        image = self.source_dir / "layout.png"
        image.write_bytes(b"not-a-real-image")
        self.add_file(image, "file-image")

        context = app.load_project_context(self.project_id)

        self.assertIn("已登记 1 份原始资料，成功提取 0 份", context)
        self.assertIn("已接收但未提取到文字", context)
        self.assertNotIn("未接收到任何原始输入材料", context)

    def test_each_agent_can_ask_only_one_question_across_the_run(self):
        run_id = "run-question-limit"
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO runs
                (id, project_id, status, trace_id, created_at)
                VALUES(?,?,?,?,?)
                """,
                (run_id, self.project_id, "运行中", "trace-question-limit", stamp),
            )
        allowed = {"取放 TPM", "软件 TPM"}
        first_batch = [
            {
                "from_agent": "取放 TPM",
                "to_agent": "软件 TPM",
                "question": "异形载具是否需要新增识别功能？",
                "reason": "最可能超出标准取放能力",
                "related_requirement": "REQ-1",
                "evidence": "E-1",
            },
            {
                "from_agent": "取放 TPM",
                "to_agent": "软件 TPM",
                "question": "是否还要新增第二个功能？",
                "reason": "次要疑点",
                "related_requirement": "REQ-2",
                "evidence": "E-2",
            },
            {
                "from_agent": "软件 TPM",
                "to_agent": "取放 TPM",
                "question": "是否需要新增取放状态接口？",
                "reason": "最可能新增接口功能",
                "related_requirement": "REQ-3",
                "evidence": "E-3",
            },
        ]

        saved = app.save_agent_questions(run_id, 3, 1, first_batch, allowed, 10)
        retry = app.save_agent_questions(run_id, 3, 2, first_batch[:1], allowed, 10)

        self.assertEqual(2, len(saved))
        self.assertEqual({"取放 TPM", "软件 TPM"}, {item["from_agent"] for item in saved})
        self.assertEqual([], retry)
        with app.connect() as db:
            counts = db.execute(
                "SELECT from_agent, COUNT(*) AS n FROM agent_messages WHERE run_id=? GROUP BY from_agent",
                (run_id,),
            ).fetchall()
        self.assertTrue(all(row["n"] == 1 for row in counts))

    def test_domain_agents_run_two_at_a_time_and_isolate_one_failure(self):
        run_id = "run-domain-concurrency"
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO runs
                (id, project_id, status, trace_id, created_at)
                VALUES(?,?,?,?,?)
                """,
                (run_id, self.project_id, "运行中", "trace-domain-concurrency", stamp),
            )
            project = db.execute(
                "SELECT * FROM projects WHERE id=?",
                (self.project_id,),
            ).fetchone()

        class FakeClient:
            def __init__(self):
                self.lock = threading.Lock()
                self.active = 0
                self.max_active = 0
                self.domain_options = []

            def chat(self, messages, **kwargs):
                if "timeout" not in kwargs:
                    return SimpleNamespace(content="[]")
                with self.lock:
                    self.active += 1
                    self.max_active = max(self.max_active, self.active)
                    self.domain_options.append(
                        (kwargs["timeout"], kwargs["max_retries"])
                    )
                try:
                    time.sleep(0.05)
                    if "A_FAIL" in messages[0]["content"]:
                        raise app.SiliconFlowError("domain timeout")
                    return SimpleNamespace(content="domain review completed")
                finally:
                    with self.lock:
                        self.active -= 1

        fake_client = FakeClient()
        specs = [
            ("A_OK", "a_ok", "review A"),
            ("A_FAIL", "a_fail", "review B"),
            ("B_OK", "b_ok", "review C"),
        ]
        with (
            patch.object(app, "DOMAIN_AGENT_SPECS", specs),
            patch.object(app, "load_role_knowledge", return_value=""),
            patch.object(app, "needs_mingmou_review", return_value=False),
            patch.object(app, "OBSIDIAN_PUBLISH_ENABLED", False),
        ):
            app.run_domain_collaboration(
                fake_client,
                project,
                run_id,
                "REQ-001 project context",
            )

        self.assertEqual(2, fake_client.max_active)
        self.assertEqual(
            [(120, 1), (120, 1), (120, 1)],
            sorted(fake_client.domain_options),
        )
        with app.connect() as db:
            rows = db.execute(
                """
                SELECT agent, status
                FROM agent_results
                WHERE run_id=? AND stage_index=3 AND agent IN ('A_OK','A_FAIL','B_OK')
                """,
                (run_id,),
            ).fetchall()
        statuses = {row["agent"]: row["status"] for row in rows}
        self.assertEqual("失败", statuses["A_FAIL"])
        self.assertEqual("已完成", statuses["A_OK"])
        self.assertEqual("已完成", statuses["B_OK"])

    def test_stage_cache_roundtrip_supports_incremental_rerun(self):
        key = app.stable_hash("cache-test", self.project_id)
        app.save_stage_cache(key, "test-stage", {"content": "cached-result"})

        cached = app.load_stage_cache(key)

        self.assertEqual({"content": "cached-result"}, cached)

    def test_evidence_critic_skips_model_when_rules_do_not_trigger(self):
        run_id = "run-rule-critic"
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO runs
                (id, project_id, status, trace_id, created_at)
                VALUES(?,?,?,?,?)
                """,
                (run_id, self.project_id, "运行中", "trace-rule-critic", stamp),
            )
            project = db.execute(
                "SELECT * FROM projects WHERE id=?", (self.project_id,)
            ).fetchone()

        class NoCallClient:
            model = "test-model"

            def chat(self, *_args, **_kwargs):
                raise AssertionError("规则质检不应调用模型")

        with patch.object(app, "OBSIDIAN_PUBLISH_ENABLED", False):
            _target, content = app.run_evidence_critic(
                NoCallClient(),
                project,
                run_id,
                "REQ-001：标准任务",
                "REQ-001｜风险等级：低｜证据：E-001｜现有能力覆盖",
            )

        self.assertIn("规则优先", content)
        self.assertIn("语义复核：否", content)

    def test_global_five_files_use_one_model_call(self):
        run_id = "run-single-global-call"
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO runs
                (id, project_id, status, trace_id, created_at)
                VALUES(?,?,?,?,?)
                """,
                (run_id, self.project_id, "运行中", "trace-single-global", stamp),
            )
            project = db.execute(
                "SELECT * FROM projects WHERE id=?", (self.project_id,)
            ).fetchone()

        class OneCallClient:
            model = "deepseek-v4-flash"

            def __init__(self):
                self.calls = []

            def chat(self, messages, **kwargs):
                self.calls.append((messages, kwargs))
                return SimpleNamespace(
                    content="# 方案评审主报告\n\n主报告内容",
                    model=self.model,
                    trace_id="trace-model",
                    usage={
                        "prompt_tokens": 100,
                        "completion_tokens": 20,
                        "total_tokens": 120,
                    },
                    finish_reason="stop",
                )

        nonstandard = (
            "非标开发项：1项\n\n"
            "## 已确认定制/非标开发\n\n"
            "| ID | 分类 | 内容 |\n|---|---|---|\n| NS-1 | 非标开发 | 新功能 |\n\n"
            "## 版本依赖配置\n\n无\n\n"
            "## 标准能力\n\n无\n\n"
            "## 待确认\n\n无\n\n"
            "## 范围外\n\n无"
        )
        fake = OneCallClient()
        with patch.object(app, "OBSIDIAN_PUBLISH_ENABLED", False):
            app.save_ai_artifact(
                project, run_id, 2, "requirements_model.md", "需求模型", "REQ-001"
            )
            app.save_ai_artifact(
                project, run_id, 3, "domain_review.md", "AI领域评审汇总", "领域风险：低"
            )
            app.save_ai_artifact(
                project, run_id, 4, "evidence_critique.md", "AI证据质检", "规则质检通过"
            )
            app.save_ai_artifact(
                project, run_id, 5, "decision_version_fit.md", "版本适配 Agent结果", "5.2.2"
            )
            app.save_ai_artifact(
                project,
                run_id,
                5,
                "decision_nonstandard_classifier.md",
                "非标判定 Agent结果",
                nonstandard,
            )
            app.save_ai_artifact(
                project, run_id, 5, "decision_effort_estimation.md", "人时估算 Agent结果", "16人时"
            )
            app.run_global_summary_outputs(fake, project, run_id)

        self.assertEqual(1, len(fake.calls))
        with app.connect() as db:
            outputs = db.execute(
                "SELECT artifact_type FROM artifacts WHERE run_id=? AND stage_index=6",
                (run_id,),
            ).fetchall()
        self.assertEqual(5, len(outputs))


class DomainAgentBoundaryTests(unittest.TestCase):
    def test_requirements_stage_is_lightweight_and_capped(self):
        self.assertEqual("轻量需求建模 Agent", app.AI_STAGES[2][0])
        self.assertIn("不要重新编写", app.AI_STAGES[2][1])
        self.assertIn("附件登记", app.AI_STAGES[2][1])
        self.assertIn("REQ ID", app.AI_STAGES[2][1])

    def test_domain_runtime_limits_are_explicit(self):
        self.assertEqual(2, app.DOMAIN_AGENT_MAX_CONCURRENCY)
        self.assertEqual(120, app.DOMAIN_AGENT_TIMEOUT_SECONDS)
        self.assertEqual(1, app.DOMAIN_AGENT_MAX_RETRIES)

    def test_software_agent_enforces_version_comparison_order(self):
        responsibilities = {
            slug: text for _name, slug, text in app.DOMAIN_AGENT_SPECS
        }
        software = responsibilities["software"]
        self.assertIn("先逐项对比5.2.2", software)
        self.assertIn("5.2.2无法满足", software)
        self.assertIn("5.3.2", software)

    def test_pick_place_replaces_hardware_and_site_review(self):
        names = {name for name, _slug, _responsibility in app.DOMAIN_AGENT_SPECS}
        slugs = {slug for _name, slug, _responsibility in app.DOMAIN_AGENT_SPECS}
        self.assertIn("取放 TPM", names)
        self.assertIn("pick_place", slugs)
        self.assertNotIn("硬件与安全 TPM", names)
        self.assertNotIn("hardware_safety", slugs)
        self.assertIn("载具", dict((slug, text) for _name, slug, text in app.DOMAIN_AGENT_SPECS)["pick_place"])

    def test_delivery_decisions_are_three_separate_agents(self):
        slugs = [slug for _name, slug, _responsibility in app.DECISION_AGENT_SPECS]
        self.assertEqual(
            ["version_fit", "nonstandard_classifier", "effort_estimation"],
            slugs,
        )
        self.assertNotIn("site_adaptation", slugs)

    def test_global_summary_owns_main_report_and_four_attachments(self):
        filenames = [filename for filename, _artifact_type, _instruction in app.GLOBAL_OUTPUT_SPECS]
        self.assertEqual(
            [
                "final_review.md",
                "version_recommendation.md",
                "custom_development_checklist.md",
                "nonstandard_development_items.md",
                "effort_recommendation.md",
            ],
            filenames,
        )


if __name__ == "__main__":
    unittest.main()
