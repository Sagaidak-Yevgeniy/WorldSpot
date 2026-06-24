#!/usr/bin/env python3
"""HTML и PDF методички WorldSpot."""

from __future__ import annotations

import html
from pathlib import Path

DOCS = Path(__file__).resolve().parent
OUTPUT_HTML = DOCS / "Разработка_игры_WorldSpot.html"
OUTPUT_PDF = DOCS / "Разработка_игры_WorldSpot.pdf"

ACCENT = "#1a6b4a"
ACCENT_LIGHT = "#d1fae5"

PRINT_CSS = f"""
@page {{
  size: A4;
  margin: 16mm 14mm 20mm 14mm;
  @bottom-center {{
    content: "Стр. " counter(page);
    font-size: 9pt;
    color: #666;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #1a1a2e;
  margin: 0;
  padding: 0;
}}
.cover {{
  text-align: center;
  padding: 48pt 24pt;
  background: {ACCENT};
  color: #fff;
  page-break-after: always;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}
.cover h1 {{ color: #fff; border: none; font-size: 26pt; margin: 0 0 12pt; }}
.cover p {{ margin: 6pt 0; font-size: 13pt; }}
.toc {{
  page-break-after: always;
  padding: 16pt 14pt 24pt;
  break-inside: avoid;
}}
.toc h2 {{
  margin: 0 0 14pt;
  font-size: 18pt;
  color: {ACCENT};
  border-bottom: 2pt solid {ACCENT_LIGHT};
  padding-bottom: 6pt;
}}
.toc ol {{ list-style: none; margin: 0; padding: 0; }}
.toc li {{
  display: flex;
  align-items: baseline;
  gap: 8pt;
  padding: 5pt 0;
  border-bottom: 1pt dotted #d1d5db;
  font-size: 10.5pt;
  break-inside: avoid;
}}
.toc-num {{ color: {ACCENT}; font-weight: bold; min-width: 18pt; }}
.toc-title {{ flex: 1; color: #1a1a2e; }}
.toc a {{ color: inherit; text-decoration: none; }}
.chapter > h1 {{
  color: {ACCENT};
  font-size: 18pt;
  border-bottom: 2pt solid {ACCENT_LIGHT};
  padding-bottom: 4pt;
  margin: 18pt 0 10pt;
  page-break-after: avoid;
}}
h2 {{ color: #2d3748; font-size: 13pt; margin: 14pt 0 6pt; page-break-after: avoid; }}
h3 {{ color: #4a5568; font-size: 11.5pt; margin: 10pt 0 4pt; }}
p {{ margin: 0 0 8pt; text-align: justify; }}
ul, ol {{ margin: 4pt 0 10pt; padding-left: 20pt; }}
li {{ margin: 3pt 0; }}
pre {{
  background: #f4f4f8;
  border: 1pt solid #ccc;
  border-left: 3pt solid {ACCENT};
  padding: 8pt 10pt;
  margin: 8pt 0 10pt;
  font-family: "Courier New", monospace;
  font-size: 8.5pt;
  line-height: 1.35;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  page-break-inside: avoid;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}
.tip {{ background: #ecfdf5; border: 1pt solid #6ee7b7; padding: 8pt 10pt; margin: 10pt 0; page-break-inside: avoid; print-color-adjust: exact; }}
.warn {{ background: #fef2f2; border: 1pt solid #fca5a5; padding: 8pt 10pt; margin: 10pt 0; page-break-inside: avoid; print-color-adjust: exact; }}
.practice {{ background: #f0fdf4; border: 1pt solid #86efac; padding: 8pt 10pt; margin: 10pt 0; page-break-inside: avoid; print-color-adjust: exact; }}
table {{ width: 100%; border-collapse: collapse; margin: 10pt 0 12pt; font-size: 10pt; page-break-inside: avoid; }}
th, td {{ border: 1pt solid #bbb; padding: 5pt 7pt; text-align: left; vertical-align: top; word-wrap: break-word; }}
th {{ background: #edf2f7; font-weight: bold; print-color-adjust: exact; }}
"""


def esc(text: str) -> str:
    return html.escape(text)


class HtmlBuilder:
    def __init__(self) -> None:
        self.parts: list[str] = []
        self.toc: list[str] = []
        self._open_ul = False
        self._section_open = False

    def _close_ul(self) -> None:
        if self._open_ul:
            self.parts.append("</ul>")
            self._open_ul = False

    def _close_section(self) -> None:
        if self._section_open:
            self.parts.append("</section>")
            self._section_open = False

    def chapter(self, title: str, toc: list) -> None:
        self._close_ul()
        self._close_section()
        toc.append(title)
        self.toc.append(title)
        n = len(toc)
        self.parts.append(f'<section class="chapter" id="ch{n}"><h1>{esc(title)}</h1>')

    def heading(self, text: str, level: int = 1) -> None:
        self._close_ul()
        tag = min(level + 1, 3)
        self.parts.append(f"<h{tag}>{esc(text)}</h{tag}>")

    def paragraph(self, text: str) -> None:
        self._close_ul()
        self.parts.append(f"<p>{esc(text)}</p>")

    def bullet(self, text: str) -> None:
        if not self._open_ul:
            self.parts.append("<ul>")
            self._open_ul = True
        self.parts.append(f"<li>{esc(text)}</li>")

    def numbered_item(self, num: int, text: str) -> None:
        self._close_ul()
        self.parts.append(f"<p><strong>{num}.</strong> {esc(text)}</p>")

    def tip(self, text: str) -> None:
        self._close_ul()
        self.parts.append(f'<div class="tip"><strong>Совет:</strong> {esc(text)}</div>')

    def warning(self, text: str) -> None:
        self._close_ul()
        self.parts.append(f'<div class="warn"><strong>Важно:</strong> {esc(text)}</div>')

    def code_block(self, code: str) -> None:
        self._close_ul()
        self.parts.append(f"<pre><code>{esc(code.rstrip())}</code></pre>")

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        self._close_ul()
        head = "".join(f"<th>{esc(h)}</th>" for h in headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows
        )
        self.parts.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")

    def exercise(self, title: str, tasks: list[str]) -> None:
        self._close_ul()
        items = "".join(f"<li>{esc(t)}</li>" for t in tasks)
        self.parts.append(
            f'<div class="practice"><strong>Практика: {esc(title)}</strong><ol>{items}</ol></div>'
        )

    def add_page(self) -> None:
        self._close_ul()

    def ln(self, *_args) -> None:
        pass

    def finish(self) -> None:
        self._close_ul()
        self._close_section()


def build_toc_html(titles: list[str]) -> str:
    return "\n".join(
        f'<li><span class="toc-num">{i}.</span>'
        f'<span class="toc-title"><a href="#ch{i}">{esc(t)}</a></span></li>'
        for i, t in enumerate(titles, 1)
    )


def validate(titles: list[str], body: str) -> None:
    if not titles:
        raise RuntimeError("Пустое оглавление")
    if body.count('<section class="chapter"') != len(titles):
        raise RuntimeError("Число глав не совпадает с оглавлением")


def build_html() -> str:
    from guide_content import write_chapters

    b = HtmlBuilder()
    toc: list[str] = []
    write_chapters(b, toc)
    b.finish()
    body = "\n".join(b.parts)
    validate(toc, body)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Разработка игры WorldSpot</title>
  <style>{PRINT_CSS}</style>
</head>
<body>
  <div class="cover">
    <h1>WorldSpot</h1>
    <p>Географическая игра в духе GeoGuessr</p>
    <p>Python + pygame · панорамы · карта · статистика · рейтинг</p>
    <p><small>Методическое пособие v1.0</small></p>
  </div>
  <div class="toc">
    <h2>Содержание</h2>
    <ol>{build_toc_html(toc)}</ol>
  </div>
  {body}
</body>
</html>"""


def write_html(path: Path | None = None) -> Path:
    path = path or OUTPUT_HTML
    path.write_text(build_html(), encoding="utf-8")
    return path
