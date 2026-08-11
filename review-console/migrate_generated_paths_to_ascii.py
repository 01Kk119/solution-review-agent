from __future__ import annotations

import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

import app


def migrate() -> list[tuple[str, str]]:
    generated = app.GENERATED_DIR.resolve()
    database = app.DB_PATH.resolve()
    backup = database.with_name(
        f"{database.stem}.before_ascii_migration_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}{database.suffix}"
    )
    if database.exists():
        shutil.copy2(database, backup)

    changes: list[tuple[str, str]] = []
    directory_names = {
        "无": app.safe_ascii_filename_component("无", "project").lower(),
        "无项目号": app.safe_ascii_filename_component("无项目号", "project").lower(),
    }
    for old_name, new_name in directory_names.items():
        source = generated / old_name
        target = generated / new_name
        if source.exists():
            if target.exists():
                raise FileExistsError(f"Migration target already exists: {target}")
            source.rename(target)
            changes.append((str(source), str(target)))

    for catalog in generated.glob("*/catalog/*.md"):
        if catalog.name.isascii():
            continue
        project_slug = catalog.parents[1].name
        date_match = re.search(r"(\d{8})", catalog.stem)
        date_code = date_match.group(1) if date_match else "unknown_date"
        target = catalog.with_name(f"{project_slug}_00_file_catalog_{date_code}.md")
        if target.exists():
            raise FileExistsError(f"Migration target already exists: {target}")
        old_path = str(catalog)
        catalog.rename(target)
        changes.append((old_path, str(target)))

    if database.exists() and changes:
        with sqlite3.connect(database, timeout=30) as db:
            for table, column in (("artifacts", "path"), ("files", "stored_path")):
                for old_path, new_path in changes:
                    db.execute(
                        f"UPDATE {table} SET {column}=REPLACE({column}, ?, ?) "
                        f"WHERE {column} LIKE ?",
                        (old_path, new_path, f"{old_path}%"),
                    )
            db.commit()
    return changes


if __name__ == "__main__":
    migrated = migrate()
    for old_path, new_path in migrated:
        print(f"{old_path} -> {new_path}")
    print(f"Migrated {len(migrated)} paths.")
