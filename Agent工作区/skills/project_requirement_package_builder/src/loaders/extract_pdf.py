# -*- coding: utf-8 -*-
"""PDF 抽取：逐页文本、表格、内嵌图片；低文本页渲染整页快照标记视觉读取。"""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from .base import (KIND_IMAGE, KIND_SNAPSHOT, KIND_TABLE, KIND_TEXT,
                   PARSE_PARTIAL, FileExtraction, Unit, sanitize_name)


def extract_pdf(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    min_px = cfg.get("min_image_px", 80)
    min_bytes = cfg.get("min_image_bytes", 3000)
    snap_below = cfg.get("snapshot_when_text_below_chars", 40)
    dpi = cfg.get("page_snapshot_dpi", 150)
    stem = sanitize_name(path.stem, 40)

    doc = fitz.open(path)
    try:
        for pno, page in enumerate(doc, start=1):
            locator = f"page {pno}"
            text = page.get_text("text").strip()
            if text:
                fx.add(Unit(locator=locator, kind=KIND_TEXT, text=text))

            # 表格识别（尽力而为，失败不影响整页）
            try:
                tabs = page.find_tables()
                for ti, tab in enumerate(tabs.tables, start=1):
                    rows = tab.extract()
                    if rows and any(any(c for c in r) for r in rows):
                        from .base import rows_to_markdown_table
                        md = rows_to_markdown_table(rows)
                        if md:
                            fx.add(Unit(locator=f"{locator} table {ti}",
                                        kind=KIND_TABLE, text=md))
            except Exception as e:  # noqa: BLE001
                fx.notes.append(f"{locator}: 表格识别失败（{e}），已跳过表格")

            # 内嵌图片
            img_count = 0
            for ii, info in enumerate(page.get_images(full=True), start=1):
                xref = info[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width < min_px or pix.height < min_px:
                        continue
                    if pix.colorspace and pix.colorspace.n > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    data = pix.tobytes("png")
                    if len(data) < min_bytes:
                        continue
                    name = f"{fx.file_id}_{stem}_p{pno}_img{ii}.png"
                    out = assets_dir / "images" / name
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(data)
                    img_count += 1
                    fx.add(Unit(locator=f"{locator} image {ii}", kind=KIND_IMAGE,
                                asset_path=f"assets/images/{name}",
                                needs_visual_reading=True,
                                context=f"页面文本前 80 字：{text[:80]}" if text else "该页无文本层"))
                except Exception as e:  # noqa: BLE001
                    fx.notes.append(f"{locator} image {ii}: 图片导出失败（{e}）")

            # 低文本页 → 整页快照（AI 视觉读取，替代 OCR）
            if len(text) < snap_below and (img_count > 0 or page.get_drawings()):
                try:
                    pix = page.get_pixmap(dpi=dpi)
                    name = f"{fx.file_id}_{stem}_p{pno}_snapshot.png"
                    out = assets_dir / "source_snapshots" / name
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(pix.tobytes("png"))
                    fx.add(Unit(locator=f"{locator}（整页快照）", kind=KIND_SNAPSHOT,
                                asset_path=f"assets/source_snapshots/{name}",
                                needs_visual_reading=True,
                                context="该页无有效文本层，内容需 AI 视觉读取"))
                except Exception as e:  # noqa: BLE001
                    fx.notes.append(f"{locator}: 页面快照失败（{e}）")
                    fx.parse_status = PARSE_PARTIAL
    finally:
        doc.close()
