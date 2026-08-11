# -*- coding: utf-8 -*-
"""输出包校验：必需文件、metadata 必填字段、证据索引合法性、Markdown 交叉核对。"""
from __future__ import annotations

import json
import re
from pathlib import Path

from evidence_builder import (crosscheck_markdown, load_evidence,
                              validate_evidence)

REQUIRED_FILES = [
    "project_requirement_package.md",
    "metadata.json",
    "evidence_index.json",
    "missing_info_checklist.md",
]
OPTIONAL_FILES = ["project_requirement_package.html"]
METADATA_REQUIRED = ["project_name", "customer_name", "region", "industry",
                     "vehicle_models", "vehicle_count", "source_files",
                     "generated_at", "skill_version", "language"]
REQUIRED_SECTIONS = [
    "## 0. 文档说明", "## 1. 项目基础信息", "## 2. 业务流程与作业流",
    "## 3. 车辆与产品形态", "## 4. 搬运对象与载具信息",
    "## 5. 取货 / 放货 / 识别场景", "## 6. 导航与现场环境",
    "## 7. 调度、接口与软件模块", "## 8. 硬件与安全相关信息",
    "## 9. 项目需求清单", "## 10. 待确认问题清单",
    "## 11. 资料侧初步风险提示", "## 12. 原始资料索引", "## 13. AI 处理日志",
]


def validate(output_dir: Path) -> tuple:
    """返回 (errors, warnings)。errors 非空则校验失败。"""
    errors, warnings = [], []

    for f in REQUIRED_FILES:
        if not (output_dir / f).exists():
            errors.append(f"缺少必需文件：{f}")
    for f in OPTIONAL_FILES:
        if not (output_dir / f).exists():
            warnings.append(f"缺少可选文件：{f}（运行 render 生成）")
    if errors:
        return errors, warnings

    # metadata
    try:
        meta = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
        for k in METADATA_REQUIRED:
            if k not in meta:
                errors.append(f"metadata.json 缺少字段：{k}")
        if meta.get("language") != "zh-CN":
            warnings.append("metadata.language 不是 zh-CN")
    except json.JSONDecodeError as e:
        errors.append(f"metadata.json 不是合法 JSON：{e}")
        meta = {}

    # manifest（若存在，用于 source_file 一致性检查）
    known_files: set = set()
    manifest_path = output_dir / "extracted" / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        known_files = {f["source_file"] for f in manifest.get("files", [])}
        known_files |= {Path(f).name for f in known_files}

    # evidence
    md_text = (output_dir / "project_requirement_package.md").read_text(encoding="utf-8")
    try:
        entries = load_evidence(output_dir / "evidence_index.json")
        errors += validate_evidence(entries, known_files)
        errors += crosscheck_markdown(md_text, entries)
        if not entries:
            warnings.append("evidence_index.json 为空——资料包缺少可追溯证据")
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"evidence_index.json 解析失败：{e}")

    # markdown 章节完整性
    for sec in REQUIRED_SECTIONS:
        if sec not in md_text:
            errors.append(f"Markdown 缺少章节：{sec}")

    # markdown 引用的本地图片是否存在
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", md_text):
        rel = m.group(1).strip()
        if rel.startswith(("http://", "https://", "data:")):
            continue
        if not (output_dir / rel).exists():
            errors.append(f"Markdown 引用的图片不存在：{rel}")

    # 模板占位/AI 注释是否清理干净
    if "{{" in md_text:
        errors.append("Markdown 中残留 {{占位符}}")
    if "<!-- AI" in md_text:
        warnings.append("Markdown 中残留 AI 指导注释，建议清理")

    return errors, warnings
