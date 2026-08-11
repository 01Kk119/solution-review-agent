# -*- coding: utf-8 -*-
"""Markdown 脚手架：从模板 + 抽取 manifest 生成草稿与自动章节。

Stage-2 的 AI 在草稿基础上完成正文；0.2 / 12 / 13 章的基础表格由这里确定性生成，
保证「输入资料范围 / 原始资料索引 / AI 处理日志」不漏文件、不靠模型记忆。
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "project_requirement_package_template.md"
CHECKLIST_TEMPLATE = SKILL_DIR / "templates" / "missing_info_checklist_template.md"

STATUS_LABEL = {
    "ok": "成功",
    "partial": "部分成功",
    "failed": "失败",
    "skipped_media": "跳过（视频/音频，预留接口）",
    "skipped_unsupported": "跳过（暂不支持的格式）",
}


def _now_iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def build_source_table(manifest: dict) -> str:
    rows = ["| # | 文件 | 类型 | 解析状态 | 主要内容判断 |",
            "|---|---|---|---|---|"]
    for i, f in enumerate(manifest.get("files", []), start=1):
        st = STATUS_LABEL.get(f["parse_status"], f["parse_status"])
        stats = f.get("stats", {})
        hint = (f"文本单元 {stats.get('text_units', 0)}，表格 {stats.get('table_units', 0)}，"
                f"图片 {stats.get('image_units', 0)}（其中需视觉读取 {stats.get('needs_visual_reading', 0)}）")
        note = "<br>（AI 补充内容判断）"
        rows.append(f"| {i} | {f['source_file']} | {f['source_type']} | {st} | {hint}{note} |")
    return "\n".join(rows)


def build_processing_log(manifest: dict) -> str:
    files = manifest.get("files", [])
    ok = [f for f in files if f["parse_status"] == "ok"]
    partial = [f for f in files if f["parse_status"] == "partial"]
    failed = [f for f in files if f["parse_status"] == "failed"]
    skipped = [f for f in files if f["parse_status"].startswith("skipped")]
    visual = sum(f.get("stats", {}).get("needs_visual_reading", 0) for f in files)
    tables = sum(f.get("stats", {}).get("table_units", 0) for f in files)
    images = sum(f.get("stats", {}).get("image_units", 0) for f in files)

    lines = [
        f"- 抽取时间：{manifest.get('generated_at', '')}，Skill 版本：{manifest.get('skill_version', '')}",
        f"- 成功解析：{len(ok)} 个文件；部分成功：{len(partial)}；失败：{len(failed)}；跳过：{len(skipped)}",
        f"- 图片提取：共 {images} 个图片/快照单元，其中 {visual} 个标记为「需 AI 视觉读取」"
        "（本 Skill 用 AI 视觉读取替代本地 OCR）",
        f"- 表格提取：共 {tables} 个表格单元（Excel sheet / PDF 表格 / Word 表格 / PPT 表格）",
    ]
    if failed:
        lines.append("- **解析失败文件（需人工处理）**：")
        for f in failed:
            lines.append(f"  - {f['source_file']}：{f.get('error', '')[:300]}")
    if partial:
        lines.append("- 部分成功文件：")
        for f in partial:
            lines.append(f"  - {f['source_file']}：{'；'.join(f.get('notes', [])[:5])}")
    if skipped:
        lines.append("- 跳过的文件：")
        for f in skipped:
            lines.append(f"  - {f['source_file']}（{STATUS_LABEL.get(f['parse_status'], f['parse_status'])}）")
    for f in files:
        for n in f.get("notes", []):
            lines.append(f"- 备注（{f['source_file']}）：{n}")
    lines.append("- 不确定项与需人工复核内容：（AI 在 Stage-2 补充）")
    return "\n".join(lines)


def scaffold(output_dir: Path, manifest: dict, project_name: str,
             skill_version: str) -> Path:
    """生成草稿 project_requirement_package.md（若已存在最终文件则不覆盖）。"""
    text = TEMPLATE.read_text(encoding="utf-8")
    text = (text.replace("{{project_name}}", project_name or "（未指定，需从资料确认）")
                .replace("{{generated_at}}", _now_iso())
                .replace("{{skill_version}}", skill_version))
    # 注入 0.2 输入资料范围表
    text = text.replace(
        "| # | 文件 | 类型 | 解析状态 | 主要内容判断 |\n|---|---|---|---|---|",
        build_source_table(manifest), 1)
    # 注入 13 章处理日志基础内容
    processing_log = build_processing_log(manifest)
    text = re.sub(
        r"(## 13\. AI 处理日志\n)",
        lambda m: m.group(1) + "\n" + processing_log + "\n",
        text,
    )
    out = output_dir / "project_requirement_package.draft.md"
    out.write_text(text, encoding="utf-8")
    return out


def scaffold_checklist(output_dir: Path, project_name: str) -> Path:
    text = CHECKLIST_TEMPLATE.read_text(encoding="utf-8")
    text = (text.replace("{{project_name}}", project_name or "（未指定）")
                .replace("{{generated_at}}", _now_iso()))
    out = output_dir / "missing_info_checklist.draft.md"
    out.write_text(text, encoding="utf-8")
    return out
