import json
import gc
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import app


class RerunReviewTests(unittest.TestCase):
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

        self.project_id = "project-1"
        self.old_run_id = "run-old"
        self.source_dir = app.UPLOAD_DIR / "vn10001"
        self.source_dir.mkdir(parents=True)
        self.source_file = self.source_dir / "input.md"
        self.source_file.write_text("# source", encoding="utf-8")
        stamp = app.now()
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO projects
                (id, project_key, name, status, risk_level, nonstandard_items,
                 source_path, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    self.project_id,
                    "vn10001",
                    "Test",
                    "已完成",
                    "高",
                    "2 项",
                    str(self.source_dir),
                    stamp,
                    stamp,
                ),
            )
            db.execute(
                """
                INSERT INTO files
                (id, project_id, kind, name, stored_path, size, created_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    "file-1",
                    self.project_id,
                    "原始资料",
                    self.source_file.name,
                    str(self.source_file),
                    self.source_file.stat().st_size,
                    stamp,
                ),
            )
            db.execute(
                """
                INSERT INTO runs(id, project_id, status, message, trace_id, created_at, finished_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (self.old_run_id, self.project_id, "已完成", "done", "trace-old", stamp, stamp),
            )

        self.generated_file = app.GENERATED_DIR / "vn10001" / self.old_run_id / "result.md"
        self.generated_file.parent.mkdir(parents=True)
        self.generated_file.write_text("# old result", encoding="utf-8")
        self.obsidian_file = (
            app.OBSIDIAN_VAULT_DIR
            / "review_outputs"
            / "vn10001"
            / "final"
            / "vn10001_final_review.md"
        )
        self.obsidian_file.parent.mkdir(parents=True)
        self.obsidian_file.write_text("# old final", encoding="utf-8")
        self.history_file = (
            self.obsidian_file.parent / "history" / "earlier" / self.obsidian_file.name
        )
        self.history_file.parent.mkdir(parents=True)
        self.history_file.write_text("# earlier final", encoding="utf-8")
        with app.connect() as db:
            db.execute(
                """
                INSERT INTO artifacts
                (id, project_id, run_id, artifact_type, title, path, status,
                 created_at, stage_index, is_final)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    "artifact-1",
                    self.project_id,
                    self.old_run_id,
                    "AI最终评审结果",
                    "result",
                    str(self.generated_file),
                    "有效",
                    stamp,
                    6,
                    1,
                ),
            )
            db.execute(
                """
                INSERT INTO run_events
                (run_id, stage_index, event_type, agent, summary, detail_json, created_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    self.old_run_id,
                    6,
                    "obsidian_publish",
                    "Obsidian Publisher",
                    "published",
                    json.dumps({"path": str(self.obsidian_file)}),
                    stamp,
                ),
            )

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(app, name, value)
        gc.collect()
        self.temporary.cleanup()

    def test_requires_confirmation(self):
        with self.assertRaises(PermissionError):
            app.prepare_rerun_and_queue(
                self.project_id, confirmed=False, mode="preserve_history"
            )
        self.assertTrue(self.generated_file.exists())
        self.assertTrue(self.source_file.exists())

    def test_preserve_history_archives_outputs_and_increments_version(self):
        new_run_id, trace_id, removed, archived, version = app.prepare_rerun_and_queue(
            self.project_id, confirmed=True, mode="preserve_history"
        )
        self.assertEqual(removed, 0)
        self.assertEqual(archived, 1)
        self.assertEqual(version, 2)
        self.assertTrue(new_run_id)
        self.assertTrue(trace_id)
        self.assertTrue(self.generated_file.exists())
        self.assertFalse(self.obsidian_file.exists())
        self.assertTrue(self.source_file.exists())
        self.assertTrue(self.history_file.exists())
        archived_current = list(
            self.obsidian_file.parent.glob(
                f"history/*/{self.obsidian_file.name}"
            )
        )
        self.assertEqual(len(archived_current), 2)
        self.assertTrue(
            any(path.read_text(encoding="utf-8") == "# old final" for path in archived_current)
        )
        with app.connect() as db:
            self.assertIsNotNone(
                db.execute("SELECT id FROM runs WHERE id=?", (self.old_run_id,)).fetchone()
            )
            new_run = db.execute("SELECT * FROM runs WHERE id=?", (new_run_id,)).fetchone()
            self.assertEqual(new_run["status"], "排队中")
            self.assertEqual(new_run["output_version"], 2)
            source = db.execute("SELECT * FROM files WHERE id='file-1'").fetchone()
            self.assertIsNotNone(source)

    def test_preserve_history_accepts_outputs_from_project_key_before_rename(self):
        with app.connect() as db:
            db.execute(
                "UPDATE projects SET project_key=? WHERE id=?",
                ("vn10001-renamed", self.project_id),
            )

        _, _, removed, archived, version = app.prepare_rerun_and_queue(
            self.project_id, confirmed=True, mode="preserve_history"
        )

        self.assertEqual(removed, 0)
        self.assertEqual(archived, 1)
        self.assertEqual(version, 2)
        self.assertFalse(self.obsidian_file.exists())
        archived_current = list(
            self.obsidian_file.parent.glob(
                f"history/*/{self.obsidian_file.name}"
            )
        )
        self.assertEqual(len(archived_current), 2)

    def test_replace_all_removes_history_and_restarts_version(self):
        new_run_id, _, removed, archived, version = app.prepare_rerun_and_queue(
            self.project_id, confirmed=True, mode="replace_all"
        )
        self.assertEqual(removed, 1)
        self.assertEqual(archived, 0)
        self.assertEqual(version, 1)
        self.assertFalse(self.generated_file.exists())
        self.assertFalse(self.obsidian_file.exists())
        self.assertFalse(self.history_file.exists())
        self.assertTrue(self.source_file.exists())
        with app.connect() as db:
            self.assertIsNone(
                db.execute("SELECT id FROM runs WHERE id=?", (self.old_run_id,)).fetchone()
            )
            new_run = db.execute("SELECT * FROM runs WHERE id=?", (new_run_id,)).fetchone()
            self.assertEqual(new_run["output_version"], 1)
            self.assertEqual(new_run["rerun_mode"], "replace_all")

    def test_replace_all_cleans_outputs_from_project_key_before_rename(self):
        with app.connect() as db:
            db.execute(
                "UPDATE projects SET project_key=? WHERE id=?",
                ("vn10001-renamed", self.project_id),
            )

        app.prepare_rerun_and_queue(
            self.project_id, confirmed=True, mode="replace_all"
        )

        self.assertFalse(self.obsidian_file.exists())
        self.assertFalse(self.history_file.exists())


if __name__ == "__main__":
    unittest.main()
