#!/usr/bin/env python3
"""Сборка HTML + PDF методички WorldSpot."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS))

OUTPUT_HTML = DOCS / "Разработка_игры_WorldSpot.html"
OUTPUT_PDF = DOCS / "Разработка_игры_WorldSpot.pdf"


def pdf_via_chrome(html_path: Path, pdf_path: Path) -> bool:
    for chrome in [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
    ]:
        if not chrome or not Path(chrome).exists():
            continue
        try:
            subprocess.run(
                [
                    chrome,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}",
                    html_path.resolve().as_uri(),
                ],
                check=True,
                capture_output=True,
                timeout=90,
            )
            return pdf_path.exists() and pdf_path.stat().st_size > 5000
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return False


def main() -> None:
    from generate_html_guide import write_html

    html_path = write_html()
    html = html_path.read_text(encoding="utf-8")
    toc = html.count('<span class="toc-title">')
    chapters = html.count('<section class="chapter"')
    print(f"HTML: {html_path}")
    print(f"  оглавление: {toc}, глав: {chapters}, код: {html.count('<pre>')}")
    if toc == 0:
        raise SystemExit("Пустое оглавление")

    if pdf_via_chrome(html_path, OUTPUT_PDF):
        print(f"PDF: {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size // 1024} КБ)")
    else:
        print("PDF: Chrome недоступен — откройте HTML в браузере → Печать → PDF")


if __name__ == "__main__":
    main()
