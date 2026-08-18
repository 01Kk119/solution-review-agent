from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def text_columns(db: sqlite3.Connection) -> list[tuple[str, str]]:
    columns: list[tuple[str, str]] = []
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    for (table,) in tables:
        for column in db.execute(f'PRAGMA table_info("{table}")'):
            name, declared_type = column[1], (column[2] or "").upper()
            if "TEXT" in declared_type:
                columns.append((table, name))
    return columns


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate persisted paths after workspace relocation.")
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    database = args.database.resolve()
    workspace = args.workspace.resolve()
    code_root = workspace / "01_Agent程序与知识库"
    data_root = workspace / "02_项目资料与运行数据"
    old_vault = workspace.parent / "risk_assessment_solution_review"

    mappings = [
        (old_vault / "agent" / "03_knowledge", code_root / "Agent知识库" / "agent" / "03_knowledge"),
        (workspace / "review-console" / "data", data_root / "工作台数据"),
        (workspace / "项目记录", data_root / "项目记录"),
        (workspace / "Order DATA" / "Order DATA" / "output", data_root / "Agent运行数据" / "output"),
        (workspace / "Order DATA" / "Order DATA" / "projects_input", data_root / "Agent运行数据" / "projects_input"),
        (workspace / "Order DATA" / "Order DATA" / "项目汇总包", data_root / "Agent运行数据" / "项目汇总包"),
        (old_vault, data_root / "Obsidian运行数据"),
    ]
    mappings = [(str(old), str(new)) for old, new in mappings]

    db = sqlite3.connect(database)
    columns = text_columns(db)
    changes: list[dict[str, object]] = []
    for table, column in columns:
        count = 0
        for old, _new in mappings:
            count += db.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" LIKE ?',
                (f"%{old}%",),
            ).fetchone()[0]
            escaped_old = old.replace("\\", "\\\\")
            count += db.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" LIKE ?',
                (f"%{escaped_old}%",),
            ).fetchone()[0]
        if count:
            changes.append({"table": table, "column": column, "matches": count})

    result: dict[str, object] = {"database": str(database), "planned_changes": changes}
    if not args.apply:
        result["applied"] = False
        print(json.dumps(result, ensure_ascii=False, indent=2))
        db.close()
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = database.with_name(f"{database.name}.before-path-migration-{stamp}.bak")
    db.commit()
    shutil.copy2(database, backup)

    updated_rows = 0
    with db:
        for table, column in columns:
            for old, new in mappings:
                cursor = db.execute(
                    f'UPDATE "{table}" SET "{column}"=REPLACE("{column}", ?, ?) '
                    f'WHERE "{column}" LIKE ?',
                    (old, new, f"%{old}%"),
                )
                updated_rows += cursor.rowcount
                escaped_old = old.replace("\\", "\\\\")
                escaped_new = new.replace("\\", "\\\\")
                cursor = db.execute(
                    f'UPDATE "{table}" SET "{column}"=REPLACE("{column}", ?, ?) '
                    f'WHERE "{column}" LIKE ?',
                    (escaped_old, escaped_new, f"%{escaped_old}%"),
                )
                updated_rows += cursor.rowcount

    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    missing = []
    for source, query in (
        ("files", "SELECT id, stored_path AS path FROM files"),
        ("artifacts", "SELECT id, path FROM artifacts"),
    ):
        for row_id, value in db.execute(query):
            if value and not Path(value).exists():
                missing.append({"source": source, "id": row_id, "path": value})
    db.close()

    result.update(
        {
            "applied": True,
            "backup": str(backup),
            "updated_rows": updated_rows,
            "integrity_check": integrity,
            "missing_paths": missing,
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if integrity == "ok" and not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
