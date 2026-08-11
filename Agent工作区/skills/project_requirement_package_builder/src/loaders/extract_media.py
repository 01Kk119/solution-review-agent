# -*- coding: utf-8 -*-
"""视频/音频：当前版本不解析，仅登记（预留接口）。

扩展点：接入转写服务后，把转写文本放入输入目录（如 06_transcripts/），
即可被 extract_txt 正常处理；本模块保持登记职责不变。
"""
from __future__ import annotations

from pathlib import Path

from .base import KIND_MEDIA, PARSE_SKIPPED_MEDIA, FileExtraction, Unit


def extract_media_stub(path: Path, fx: FileExtraction, assets_dir: Path, cfg: dict) -> None:
    fx.parse_status = PARSE_SKIPPED_MEDIA
    size_mb = path.stat().st_size / (1024 * 1024)
    fx.add(Unit(locator="整个文件", kind=KIND_MEDIA,
                text=f"视频/音频文件（{size_mb:.1f} MB），当前版本不解析。"
                     f"如有对应转写文本/会议纪要，请一并放入输入目录。",
                context="预留接口：后续可接入转写服务"))
    fx.notes.append("视频/音频解析未启用（预留接口），仅登记文件")
