from pathlib import Path


def test_markdown_preview_is_rendered_and_escaped():
    root = Path(__file__).parent
    app_js = (root / "static" / "app.js").read_text(encoding="utf-8")
    css = (root / "static" / "minimal.css").read_text(encoding="utf-8")
    html = (root / "static" / "index.html").read_text(encoding="utf-8")

    assert "function markdownToSafeHtml(markdown)" in app_js
    assert 'data.preview_type==="text"&&data.extension==="MD"' in app_js
    assert 'article.className="preview-markdown"' in app_js
    assert "const inlineMarkdown=text=>esc(text)" in app_js
    assert "markdown-table-wrap" in app_js
    assert ".preview-markdown table" in css
    assert ".preview-markdown blockquote" in css
    assert "/app.js?v=23" in html
