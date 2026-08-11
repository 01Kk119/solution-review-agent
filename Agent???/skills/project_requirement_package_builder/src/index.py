#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""project_requirement_package_builder CLI —— 方案侧结构化资料包生成 Skill。

Stage-1/3 为确定性代码；Stage-2（结构化转写正文）由 Claude 按 SKILL.md 完成。

用法：
  python3 src/index.py extract  --input ./input_project --output ./output_project \
                                [--project-name "XXX项目"] [--language zh-CN]
  python3 src/index.py scaffold --output ./output_project [--project-name "XXX项目"]
  python3 src/index.py render   --output ./output_project
  python3 src/index.py validate --output ./output_project
  python3 src/index.py run      --input ./input_project --output ./output_project \
                                [--project-name "XXX项目"]
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import traceback
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SKILL_DIR = SRC_DIR.parent
sys.path.insert(0, str(SRC_DIR))

import yaml  # noqa: E402

from loaders import EXTRACTORS  # noqa: E402
from loaders.base import (PARSE_FAILED, PARSE_SKIPPED_UNSUPPORTED,  # noqa: E402
                          FileExtraction, save_json)

SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def load_config(path: Path = None) -> dict:
    cfg_path = path or (SKILL_DIR / "config.yaml")
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def now_iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- extract

def cmd_extract(args) -> int:
    cfg = load_config(Path(args.config) if args.config else None)
    ext_cfg = cfg.get("extraction", {})
    media_exts = set(ext_cfg.get("media_extensions", []))
    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    if not input_dir.is_dir():
        print(f"[错误] 输入目录不存在：{input_dir}", file=sys.stderr)
        return 2

    extracted_dir = output_dir / cfg["output"].get("extracted_dirname", "extracted")
    assets_dir = output_dir / cfg["output"].get("assets_dirname", "assets")
    extracted_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 收集文件（跳过隐藏文件与输出目录自身）
    all_files = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file()
        and p.name not in SKIP_NAMES
        and not p.name.startswith("~$")
        and not any(part.startswith(".") for part in p.relative_to(input_dir).parts)
        and output_dir not in p.parents and p != output_dir
    )
    if not all_files:
        print(f"[错误] 输入目录中没有可处理的文件：{input_dir}", file=sys.stderr)
        return 2

    manifest_files = []
    for i, path in enumerate(all_files, start=1):
        fid = f"F{i:02d}"
        # Store source paths with POSIX separators so manifests are stable on
        # Windows, macOS, and Linux. The paths are logical project-relative
        # identifiers, not local filesystem paths.
        rel = path.relative_to(input_dir).as_posix()
        suffix = path.suffix.lower()
        print(f"[{fid}] {rel}", flush=True)

        if suffix in media_exts:
            from loaders.extract_media import extract_media_stub
            source_type, extractor = "media", extract_media_stub
        elif suffix in EXTRACTORS:
            source_type, extractor = EXTRACTORS[suffix]
        else:
            source_type, extractor = suffix.lstrip(".") or "unknown", None

        fx = FileExtraction(file_id=fid, source_file=rel, source_type=source_type)
        if extractor is None:
            fx.parse_status = PARSE_SKIPPED_UNSUPPORTED
            fx.notes.append(
                f"暂不支持的格式：{suffix}。若为旧版 Office（.xls/.doc/.ppt），"
                "请另存为 .xlsx/.docx/.pptx 后重新运行")
        else:
            try:
                extractor(path, fx, assets_dir, ext_cfg)
            except Exception:  # noqa: BLE001 —— 单文件失败不允许中断整体流程
                fx.parse_status = PARSE_FAILED
                fx.error = traceback.format_exc(limit=3)
                print(f"    !! 解析失败（已记录，不中断）：{path.name}", file=sys.stderr)

        save_json(extracted_dir / f"{fid}.json", fx.to_dict())
        entry = {
            "file_id": fid, "source_file": rel, "source_type": source_type,
            "parse_status": fx.parse_status, "error": fx.error,
            "stats": fx.stats(), "notes": fx.notes,
            "extracted_json": f"extracted/{fid}.json",
        }
        manifest_files.append(entry)

    totals = {
        "files": len(manifest_files),
        "ok": sum(1 for f in manifest_files if f["parse_status"] == "ok"),
        "partial": sum(1 for f in manifest_files if f["parse_status"] == "partial"),
        "failed": sum(1 for f in manifest_files if f["parse_status"] == "failed"),
        "skipped": sum(1 for f in manifest_files if f["parse_status"].startswith("skipped")),
        "units": sum(f["stats"]["units"] for f in manifest_files),
        "needs_visual_reading": sum(f["stats"]["needs_visual_reading"] for f in manifest_files),
    }
    manifest = {
        "skill_name": cfg.get("skill_name"),
        "skill_version": str(cfg.get("skill_version", "")),
        "generated_at": now_iso(),
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "project_name": args.project_name or "",
        "language": args.language or cfg.get("language", "zh-CN"),
        "totals": totals,
        "files": manifest_files,
    }
    save_json(extracted_dir / "manifest.json", manifest)
    print(f"\n抽取完成：{totals['ok']} 成功 / {totals['partial']} 部分 / "
          f"{totals['failed']} 失败 / {totals['skipped']} 跳过；"
          f"共 {totals['units']} 个内容单元，"
          f"{totals['needs_visual_reading']} 个需 AI 视觉读取。")
    print(f"manifest：{extracted_dir / 'manifest.json'}")
    return 0


# ---------------------------------------------------------------- scaffold

def cmd_scaffold(args) -> int:
    cfg = load_config(Path(args.config) if args.config else None)
    output_dir = Path(args.output).resolve()
    manifest_path = output_dir / cfg["output"].get("extracted_dirname", "extracted") / "manifest.json"
    if not manifest_path.exists():
        print("[错误] 找不到 manifest.json，请先运行 extract", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from markdown_builder import scaffold, scaffold_checklist
    name = args.project_name or manifest.get("project_name", "")
    draft = scaffold(output_dir, manifest, name, str(cfg.get("skill_version", "")))
    checklist = scaffold_checklist(output_dir, name)
    print(f"草稿已生成：\n  {draft}\n  {checklist}")
    print("下一步：由 AI（Claude，按 SKILL.md）完成正文，另存为 "
          "project_requirement_package.md / missing_info_checklist.md")
    return 0


# ---------------------------------------------------------------- render

def cmd_render(args) -> int:
    cfg = load_config(Path(args.config) if args.config else None)
    output_dir = Path(args.output).resolve()
    md = output_dir / cfg["output"]["markdown_filename"]
    if not md.exists():
        print(f"[错误] 找不到 {md.name}，无法渲染 HTML", file=sys.stderr)
        return 2
    from html_builder import render_html
    out = render_html(md, output_dir / cfg["output"]["html_filename"])
    print(f"HTML 已生成：{out}")
    return 0


# ---------------------------------------------------------------- validate

def cmd_validate(args) -> int:
    output_dir = Path(args.output).resolve()
    from validate_output import validate
    errors, warnings = validate(output_dir)
    for w in warnings:
        print(f"[警告] {w}")
    for e in errors:
        print(f"[错误] {e}")
    if errors:
        print(f"\n校验失败：{len(errors)} 个错误，{len(warnings)} 个警告")
        return 1
    print(f"\n校验通过（{len(warnings)} 个警告）")
    return 0


# ---------------------------------------------------------------- run

AI_STEP_HINT = """
================= 下一步（Stage-2，由 AI 完成正文） =================
抽取与草稿已完成。请在 Claude Code 中执行本 Skill 的结构化转写步骤：

  1. 打开本项目，让 Claude 读取：
       {skill}/SKILL.md            —— 工作流程与防幻觉规则
       {out}/extracted/manifest.json
  2. Claude 按 SKILL.md 通读 extracted/*.json 与需视觉读取的 assets 图片，
     在 draft 基础上产出：
       project_requirement_package.md / metadata.json /
       evidence_index.json / missing_info_checklist.md
  3. 然后回到命令行执行：
       python3 "{src}/index.py" render   --output "{out}"
       python3 "{src}/index.py" validate --output "{out}"
======================================================================
"""


def cmd_run(args) -> int:
    rc = cmd_extract(args)
    if rc != 0:
        return rc
    rc = cmd_scaffold(args)
    if rc != 0:
        return rc
    cfg = load_config(Path(args.config) if args.config else None)
    output_dir = Path(args.output).resolve()
    final_md = output_dir / cfg["output"]["markdown_filename"]
    if final_md.exists():
        rc = cmd_render(args)
        rc2 = cmd_validate(args)
        return rc or rc2
    print(AI_STEP_HINT.format(skill=SKILL_DIR, out=output_dir, src=SRC_DIR))
    return 0


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="project_requirement_package_builder",
        description="方案握手会资料 → 结构化项目订单原始资料包")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(p, need_input=False):
        if need_input:
            p.add_argument("--input", required=True, help="项目资料输入目录")
        p.add_argument("--output", required=True, help="资料包输出目录")
        p.add_argument("--project-name", default="", help="项目名称")
        p.add_argument("--language", default="", help="输出语言（默认 zh-CN）")
        p.add_argument("--config", default="", help="自定义 config.yaml 路径")

    add_common(sub.add_parser("extract", help="Stage-1：解析全部资料为结构化单元"), True)
    add_common(sub.add_parser("scaffold", help="从 manifest 生成 Markdown 草稿"))
    add_common(sub.add_parser("render", help="Stage-3：Markdown 渲染 HTML"))
    add_common(sub.add_parser("validate", help="Stage-3：校验输出包完整性与证据一致性"))
    add_common(sub.add_parser("run", help="extract + scaffold（+ 已有正文时 render/validate）"), True)

    args = ap.parse_args(argv)
    return {"extract": cmd_extract, "scaffold": cmd_scaffold, "render": cmd_render,
            "validate": cmd_validate, "run": cmd_run}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
