# -*- coding: utf-8 -*-
"""MD / TXT / HTML 抽取。

- Markdown：按标题切分，locator 为标题路径。
- TXT（含会议转写）：按行分块，locator 为行区间；文本中的时间戳保留，可作细粒度证据。
- HTML：剥离标签取正文。
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from .base import KIND_TEXT, FileExtraction, Unit


class _HTMLText(HTMLParser):
    SKIP = {"script", "style"}

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.parts: list = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def _read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_bytes().decode("utf-8", errors="replace")


def extract_markdown(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    text = _read_text(path)
    # 按 1-3 级标题切分；无标题则整体一个单元
    parts = re.split(r"(?m)^(#{1,3} .+)$", text)
    if len(parts) == 1:
        _chunk_plain(text, fx, cfg)
        return
    preamble = parts[0].strip()
    if preamble:
        fx.add(Unit(locator="文首（无标题段）", kind=KIND_TEXT, text=preamble))
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        title = heading.lstrip("#").strip()
        fx.add(Unit(locator=f"章节「{title}」", kind=KIND_TEXT,
                    text=(heading + "\n" + body).strip()))


def _chunk_plain(text: str, fx: FileExtraction, cfg: dict) -> None:
    chunk = cfg.get("txt_chunk_lines", 80)
    lines = text.splitlines()
    for start in range(0, len(lines), chunk):
        seg = "\n".join(lines[start:start + chunk]).strip()
        if not seg:
            continue
        # 若块内含 00:12:35 式时间戳，则在 locator 中标出首个时间戳便于引用
        m = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", seg)
        ts = f"，首个时间戳 {m.group(1)}" if m else ""
        fx.add(Unit(locator=f"行 {start + 1}-{min(start + chunk, len(lines))}{ts}",
                    kind=KIND_TEXT, text=seg))


def extract_txt(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    _chunk_plain(_read_text(path), fx, cfg)


def extract_html(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    parser = _HTMLText()
    parser.feed(_read_text(path))
    _chunk_plain("\n".join(parser.parts), fx, cfg)
