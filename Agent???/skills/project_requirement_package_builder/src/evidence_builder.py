# -*- coding: utf-8 -*-
"""证据索引工具：加载/校验 evidence_index.json，并与 Markdown 交叉核对。"""
from __future__ import annotations

import json
import re
from pathlib import Path

EVIDENCE_ID_RE = re.compile(r"\bE\d{3,}\b")
VALID_CONFIDENCE = {"原文明确", "会议口头信息", "AI归类", "AI推断待确认"}
REQUIRED_FIELDS = ["id", "source_file", "source_type", "page_or_slide", "extracted_text"]


def load_evidence(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("evidence_index.json 必须是数组")
    return data


def validate_evidence(entries: list, known_source_files: set) -> list:
    """返回问题列表（空 = 通过）。"""
    problems, seen = [], set()
    for i, e in enumerate(entries):
        for f in REQUIRED_FIELDS:
            if not e.get(f):
                problems.append(f"条目 {i}（{e.get('id', '?')}）缺少字段 {f}")
        eid = e.get("id", "")
        if eid in seen:
            problems.append(f"证据编号重复：{eid}")
        seen.add(eid)
        if eid and not re.fullmatch(r"E\d{3,}", eid):
            problems.append(f"证据编号格式不合法：{eid}（应为 E001 形式）")
        conf = e.get("confidence")
        if conf and conf not in VALID_CONFIDENCE:
            problems.append(f"{eid}: confidence 取值不合法：{conf}")
        sf = e.get("source_file", "")
        if known_source_files and sf and sf not in known_source_files:
            problems.append(f"{eid}: source_file 不在抽取清单中：{sf}")
    return problems


def crosscheck_markdown(md_text: str, entries: list) -> list:
    """核对 Markdown 中引用的证据编号都存在于索引中；返回问题列表。"""
    ids_in_index = {e.get("id") for e in entries}
    ids_in_md = set(EVIDENCE_ID_RE.findall(md_text))
    missing = sorted(ids_in_md - ids_in_index)
    return [f"Markdown 引用了索引中不存在的证据编号：{m}" for m in missing]
