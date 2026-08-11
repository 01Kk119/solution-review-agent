# -*- coding: utf-8 -*-
"""文件类型 → 抽取器 分发表。"""
from .extract_docx import extract_docx
from .extract_excel import extract_excel
from .extract_images import extract_image_file
from .extract_media import extract_media_stub
from .extract_pdf import extract_pdf
from .extract_pptx import extract_pptx
from .extract_text import extract_html, extract_markdown, extract_txt

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

EXTRACTORS = {
    ".pptx": ("pptx", extract_pptx),
    ".pdf": ("pdf", extract_pdf),
    ".xlsx": ("xlsx", extract_excel),
    ".xlsm": ("xlsx", extract_excel),
    ".docx": ("docx", extract_docx),
    ".md": ("md", extract_markdown),
    ".markdown": ("md", extract_markdown),
    ".txt": ("txt", extract_txt),
    ".html": ("html", extract_html),
    ".htm": ("html", extract_html),
}
for _ext in IMAGE_EXTS:
    EXTRACTORS[_ext] = ("image", extract_image_file)
