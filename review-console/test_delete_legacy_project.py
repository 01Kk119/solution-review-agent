import gc
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from urllib.request import Request, urlopen

import app


class DeleteLegacyProjectTests(unittest.TestCase):
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
            )
        }
        app.DATA_DIR = self.root / "data"
        app.UPLOAD_DIR = app.DATA_DIR / "uploads"
        app.GENERATED_DIR = app.DATA_DIR / "generated"
        app.UPLOAD_CHUNK_DIR = app.DATA_DIR / "upload_chunks"
        app.DB_PATH = app.DATA_DIR / "review_console.db"
        app.SOURCE_PROJECTS = self.root / "项目记录"
        app.OBSIDIAN_VAULT_DIR = self.root / "vault"

        self.legacy_dir = app.SOURCE_PROJECTS / "0727,F客户"
        self.legacy_dir.mkdir(parents=True)
        (self.legacy_dir / "proposal.txt").write_text("source", encoding="utf-8")
        app.init_db()

        with app.connect() as db:
            project = db.execute(
                "SELECT * FROM projects WHERE project_key=?", ("0727",)
            ).fetchone()
        self.project_id = project["id"]
        self.upload_dir = Path(project["source_path"])

        self.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        for name, value in self.originals.items():
            setattr(app, name, value)
        gc.collect()
        self.temporary.cleanup()

    def test_delete_removes_original_folder_and_prevents_reimport(self):
        request = Request(
            f"http://127.0.0.1:{self.server.server_port}/api/projects/{self.project_id}",
            method="DELETE",
        )
        with urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))

        self.assertTrue(payload["ok"])
        self.assertFalse(self.legacy_dir.exists())
        self.assertFalse(self.upload_dir.exists())
        with app.connect() as db:
            count = db.execute(
                "SELECT COUNT(*) FROM projects WHERE project_key=?", ("0727",)
            ).fetchone()[0]
        self.assertEqual(0, count)

        app.import_existing_projects()
        with app.connect() as db:
            count = db.execute(
                "SELECT COUNT(*) FROM projects WHERE project_key=?", ("0727",)
            ).fetchone()[0]
        self.assertEqual(0, count)


if __name__ == "__main__":
    unittest.main()
