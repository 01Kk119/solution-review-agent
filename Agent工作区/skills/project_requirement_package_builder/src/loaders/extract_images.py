# -*- coding: utf-8 -*-
"""独立图片文件：复制到 assets 并标记需 AI 视觉读取（分类/OCR/说明由 Stage-2 完成）。"""
from __future__ import annotations

import shutil
from pathlib import Path

from .base import KIND_IMAGE, FileExtraction, Unit, sanitize_name


def extract_image_file(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    name = f"{fx.file_id}_{sanitize_name(path.stem, 50)}{path.suffix.lower()}"
    out = assets_dir / "images" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, out)
    fx.add(Unit(locator="整图", kind=KIND_IMAGE,
                asset_path=f"assets/images/{name}",
                needs_visual_reading=True,
                context="独立图片文件，需 AI 视觉读取并分类"
                        "（layout/载具/现场/流程图/货架/托盘/设备/截图）"))
