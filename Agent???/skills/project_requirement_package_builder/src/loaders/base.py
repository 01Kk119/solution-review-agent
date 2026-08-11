# -*- coding: utf-8 -*-
"""抽取单元数据模型与公共工具。

Stage-1（确定性抽取）把每个源文件转成一组 Unit（带定位符的内容单元），
写入 extracted/{file_id}.json，供 Stage-2（AI 结构化转写）读取并引用为证据。
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# 内容单元类型
KIND_TEXT = "text"
KIND_TABLE = "table"
KIND_IMAGE = "image"
KIND_NOTE = "note"          # PPT speaker notes
KIND_SNAPSHOT = "snapshot"  # 整页快照（无文本层 PDF 等，需 AI 视觉读取）
KIND_MEDIA = "media"        # 视频/音频，仅登记

PARSE_OK = "ok"
PARSE_PARTIAL = "partial"
PARSE_FAILED = "failed"
PARSE_SKIPPED_MEDIA = "skipped_media"
PARSE_SKIPPED_UNSUPPORTED = "skipped_unsupported"


@dataclass
class Unit:
    """一个可被引用的最小内容单元。

    locator 是证据定位符，如：
      "slide 12" / "page 7" / "sheet 装卸车（Truck）" / "sheet 基本信息!R12"
      "段落 35（Heading: Project Information）" / "行 1-80" / "整图"
    """
    locator: str
    kind: str
    text: str = ""
    asset_path: str = ""            # 相对输出根目录，如 assets/images/F02_p3_img1.png
    needs_visual_reading: bool = False
    context: str = ""               # 上下文（如所属标题链、所在 sheet 等）

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        # 精简：空字段不写，减小 JSON 体积
        return {k: v for k, v in d.items() if v not in ("", False, None)}


@dataclass
class FileExtraction:
    """单个源文件的抽取结果。"""
    file_id: str
    source_file: str                # 相对输入根目录的路径
    source_type: str
    parse_status: str = PARSE_OK
    error: str = ""
    units: list = field(default_factory=list)
    notes: list = field(default_factory=list)   # 解析过程备注（截断、合并单元格等）

    def add(self, unit: Unit) -> None:
        self.units.append(unit)

    def stats(self) -> dict:
        return {
            "units": len(self.units),
            "text_units": sum(1 for u in self.units if u.kind == KIND_TEXT),
            "table_units": sum(1 for u in self.units if u.kind == KIND_TABLE),
            "image_units": sum(1 for u in self.units if u.kind in (KIND_IMAGE, KIND_SNAPSHOT)),
            "needs_visual_reading": sum(1 for u in self.units if u.needs_visual_reading),
            "text_chars": sum(len(u.text) for u in self.units),
        }

    def to_dict(self) -> dict:
        return {
            "file_id": self.file_id,
            "source_file": self.source_file,
            "source_type": self.source_type,
            "parse_status": self.parse_status,
            "error": self.error,
            "stats": self.stats(),
            "notes": self.notes,
            "units": [u.to_dict() for u in self.units],
        }


def sanitize_name(name: str, max_len: int = 60) -> str:
    """把任意文件名/定位符转成安全的资产文件名片段。"""
    name = unicodedata.normalize("NFKC", name)
    name = re.sub(r"[^\w一-鿿.-]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("._")
    if len(name) > max_len:
        digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
        name = name[:max_len] + "_" + digest
    return name or "unnamed"


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def rows_to_markdown_table(rows: list, max_cols: Optional[int] = None) -> str:
    """把二维数组转成 Markdown 表格。None → 空串；管道符转义。"""
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    if max_cols:
        width = min(width, max_cols)

    def fmt_cell(v) -> str:
        if v is None:
            return ""
        s = str(v).replace("\r", " ").replace("\n", "<br>")
        return s.replace("|", "\\|").strip()

    norm = [[fmt_cell(c) for c in (list(r) + [None] * width)[:width]] for r in rows]
    header = norm[0]
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join(["---"] * width) + "|"]
    for r in norm[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)
