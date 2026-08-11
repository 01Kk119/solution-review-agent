# -*- coding: utf-8 -*-
"""Markdown → HTML 渲染：内嵌样式、锚点目录，适合内部评审阅读，无外部依赖资源。"""
from __future__ import annotations

from pathlib import Path
import html
import re

try:
    import markdown
except ModuleNotFoundError:  # pragma: no cover - exercised only without dependency
    markdown = None

CSS = """
:root { --ink:#1e2430; --muted:#5c6672; --line:#dde3ea; --accent:#b3282d; --bg:#ffffff; }
* { box-sizing: border-box; }
body { margin:0; padding:0 16px 80px; background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB",
  "Microsoft YaHei","Segoe UI",sans-serif; line-height:1.75; font-size:15px; }
main { max-width: 1020px; margin: 0 auto; }
h1 { font-size:1.9em; border-bottom:3px solid var(--accent); padding-bottom:.3em; }
h2 { font-size:1.45em; margin-top:2.2em; border-bottom:1px solid var(--line);
     padding-bottom:.25em; }
h3 { font-size:1.15em; margin-top:1.8em; }
h4 { font-size:1.02em; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
blockquote { margin:1em 0; padding:.5em 1em; border-left:4px solid var(--accent);
  background:#faf6f3; color:var(--muted); }
code { background:#f2f4f7; padding:.15em .4em; border-radius:4px; font-size:.9em; }
pre { background:#f2f4f7; padding:12px; border-radius:8px; overflow-x:auto; }
.tablewrap { overflow-x:auto; margin:1em 0; }
table { border-collapse:collapse; width:100%; font-size:.92em; }
th, td { border:1px solid var(--line); padding:6px 10px; text-align:left;
  vertical-align:top; }
th { background:#f5f7fa; white-space:nowrap; }
tr:nth-child(even) td { background:#fbfcfe; }
img { max-width:100%; height:auto; border:1px solid var(--line); border-radius:6px;
  margin:.5em 0; }
.toc { background:#f7f9fb; border:1px solid var(--line); border-radius:10px;
  padding:14px 22px; margin:1.5em 0; }
.toc ul { margin:.2em 0; padding-left:1.2em; }
.toc > ul { column-count:2; column-gap:2em; }
.toc a { color:var(--ink); }
hr { border:none; border-top:1px solid var(--line); margin:2.5em 0; }
@media (max-width:760px){ .toc > ul { column-count:1; } body { font-size:14px; } }
@media print { .toc { display:none; } body { padding:0; } }
"""


def render_html(md_path: Path, html_path: Path, title: str = "") -> Path:
    text = md_path.read_text(encoding="utf-8")
    if markdown is not None:
        md = markdown.Markdown(
            extensions=["tables", "toc", "fenced_code", "sane_lists", "attr_list"],
            extension_configs={"toc": {"toc_depth": "1-3", "title": "目录"}},
        )
        body = md.convert(text)
        toc = getattr(md, "toc", "")
    else:
        body, toc = _render_basic_markdown(text)
    # 表格包一层横向滚动容器，避免宽表撑破页面
    body = body.replace("<table>", '<div class="tablewrap"><table>')
    body = body.replace("</table>", "</table></div>")
    if not title:
        title = (md_path.stem if not text.lstrip().startswith("# ")
                 else text.lstrip().splitlines()[0].lstrip("# ").strip())
    html = (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{title}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<main>\n"
        f"<div class=\"toc\">{toc}</div>\n{body}\n</main>\n</body>\n</html>\n"
    )
    html_path.write_text(html, encoding="utf-8")
    return html_path


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip().lower())
    return slug.strip("-") or "section"


def _render_basic_markdown(text: str) -> tuple[str, str]:
    """Small fallback renderer for clean review output when python-markdown is
    not installed. It handles headings, paragraphs, bullets, and simple tables;
    install `markdown` for full fenced-code/toc/attribute support.
    """
    lines = text.splitlines()
    out: list[str] = []
    toc_items: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            label = heading.group(2).strip()
            anchor = _slug(label)
            out.append(f'<h{level} id="{anchor}">{html.escape(label)}</h{level}>')
            if level <= 3:
                toc_items.append(f'<li><a href="#{anchor}">{html.escape(label)}</a></li>')
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(_render_basic_table(table_lines))
            continue

        if line.lstrip().startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                item = lines[i].lstrip()[2:].strip()
                out.append(f"<li>{html.escape(item)}</li>")
                i += 1
            out.append("</ul>")
            continue

        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("|"):
            if re.match(r"^(#{1,6})\s+", lines[i]) or lines[i].lstrip().startswith("- "):
                break
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{html.escape(' '.join(para))}</p>")

    toc = "<ul>" + "".join(toc_items) + "</ul>" if toc_items else ""
    return "\n".join(out), toc


def _render_basic_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head = "<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in rows[0]) + "</tr>"
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>"
        for row in rows[1:]
    )
    return f"<table><thead>{head}</thead><tbody>{body}</tbody></table>"
