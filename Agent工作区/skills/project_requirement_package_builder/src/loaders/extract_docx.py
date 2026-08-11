# -*- coding: utf-8 -*-
"""DOCX 抽取：按文档顺序输出段落（带标题链上下文）、表格、内嵌图片。"""
from __future__ import annotations

from pathlib import Path

import docx
from docx.document import Document as _Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import (KIND_IMAGE, KIND_TABLE, KIND_TEXT, FileExtraction, Unit,
                   rows_to_markdown_table, sanitize_name)


def _iter_block_items(parent):
    """按文档顺序迭代段落与表格。"""
    body = parent.element.body if isinstance(parent, _Document) else parent._element
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _heading_level(par: Paragraph):
    name = (par.style.name or "") if par.style else ""
    if name.lower().startswith("heading"):
        try:
            return int(name.split()[-1])
        except ValueError:
            return 1
    if name == "Title":
        return 0
    return None


def _para_images(par: Paragraph, doc, fx, assets_dir: Path, stem: str,
                 counter: list, min_bytes: int, heading_chain: str):
    """导出段落内嵌图片（w:drawing 里的 blip 引用）。"""
    for blip in par._element.findall(".//" + qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if not rid:
            continue
        try:
            part = doc.part.related_parts[rid]
            data = part.blob
            if len(data) < min_bytes:
                continue
            counter[0] += 1
            ext = Path(part.partname).suffix.lstrip(".") or "png"
            name = f"{fx.file_id}_{stem}_img{counter[0]}.{ext}"
            out = assets_dir / "images" / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            fx.add(Unit(locator=f"图片 {counter[0]}（段落附近：{heading_chain or '文档开头'}）",
                        kind=KIND_IMAGE,
                        asset_path=f"assets/images/{name}",
                        needs_visual_reading=True,
                        context=f"所在章节：{heading_chain or '未知'}"))
        except Exception as e:  # noqa: BLE001
            fx.notes.append(f"图片 rId={rid}: 导出失败（{e}）")


def extract_docx(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    min_bytes = cfg.get("min_image_bytes", 3000)
    stem = sanitize_name(path.stem, 40)
    doc = docx.Document(str(path))

    chain: list = []            # [(level, title)]
    buf: list = []              # 当前标题下累积的段落
    buf_start = 1
    pidx = 0
    tidx = 0
    img_counter = [0]

    def chain_str() -> str:
        return " > ".join(t for _, t in chain)

    def flush():
        nonlocal buf, buf_start
        text = "\n".join(buf).strip()
        if text:
            fx.add(Unit(locator=f"段落 {buf_start}-{pidx}",
                        kind=KIND_TEXT, text=text, context=chain_str()))
        buf = []
        buf_start = pidx + 1

    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            pidx += 1
            lvl = _heading_level(block)
            txt = block.text.strip()
            _para_images(block, doc, fx, assets_dir, stem, img_counter,
                         min_bytes, chain_str())
            if lvl is not None and txt:
                flush()
                while chain and chain[-1][0] >= lvl:
                    chain.pop()
                chain.append((lvl, txt))
                fx.add(Unit(locator=f"段落 {pidx}（标题 H{lvl}）", kind=KIND_TEXT,
                            text=("#" * max(lvl, 1)) + " " + txt, context=chain_str()))
                buf_start = pidx + 1
            elif txt:
                buf.append(txt)
        else:  # Table
            flush()
            tidx += 1
            rows = [[c.text.strip() for c in r.cells] for r in block.rows]
            md = rows_to_markdown_table(rows)
            if md:
                fx.add(Unit(locator=f"表格 {tidx}", kind=KIND_TABLE, text=md,
                            context=chain_str()))
    flush()
