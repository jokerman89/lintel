#!/usr/bin/env python3
# component: pdf-html-preparation
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: existing Markdown converter; owned local inputs; no browser, installation or PDF rendering
# last_intent_review: 2026-09-22
"""Prepare explicit print HTML without discarding source or inventing a Markdown parser."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
from html import escape
from html.parser import HTMLParser
import importlib.metadata
import json
from pathlib import Path
import re
import sys
from typing import Any

SOURCE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE / "lib"))
from context_safety import atomic_write, checked_root, read_owned, selector_path  # noqa: E402
from profile_context import parse_manifest  # noqa: E402


class PreparationError(ValueError):
    pass


class DocumentHead(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.head_ends: list[int] = []
        self.in_title = False
        self.title: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            line, column = self.getpos()
            self.head_ends.append(sum(len(part) for part in self.text.splitlines(keepends=True)[:line - 1]) + column)
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title.append(data)


def _css_text(text: str) -> str:
    return '"' + "".join(
        f"\\{ord(char):x} " if char in '\\\"<>\r\n' or ord(char) < 32 else char
        for char in text
    ) + '"'


def _margin_content(text: str, title: str, date_text: str) -> str:
    pieces = re.split(r"(\{\{[a-z]+\}\})", text)
    values = {"{{title}}": _css_text(title), "{{date}}": _css_text(date_text),
              "{{page}}": "counter(page)", "{{total}}": "counter(pages)"}
    output = []
    for piece in pieces:
        if piece.startswith("{{"):
            if piece not in values:
                raise PreparationError(f"Unsupported header/footer placeholder: {piece}")
            output.append(values[piece])
        elif piece:
            output.append(_css_text(piece))
    return " ".join(output) or '""'


def prepare_document(
    text: str, *, input_format: str, paper: str = "a4", orientation: str = "portrait",
    header_footer: dict[str, str] | None = None, print_css: str = "",
    no_background: bool = False, title: str = "", date_text: str | None = None,
) -> tuple[str, dict[str, Any]]:
    if not text.strip():
        raise PreparationError("Input is empty")
    if paper not in ("a4", "letter", "custom") or orientation not in ("portrait", "landscape"):
        raise PreparationError("Unsupported paper/orientation")
    if paper == "custom" and (not print_css.strip() or not re.search(r"@page\b", print_css, re.I)):
        raise PreparationError("Custom paper requires explicit @page print CSS; actual dimensions still need inspection")
    if re.search(r"</style\b", print_css, re.I):
        raise PreparationError("Print CSS cannot close its style element")
    headers = {} if header_footer is None else header_footer
    if not isinstance(headers, dict) or set(headers) - {"header", "footer"} \
            or any(not isinstance(value, str) for value in headers.values()):
        raise PreparationError("Header/footer data accepts only header and footer strings")
    if input_format == "markdown":
        try:
            from markdown_it import MarkdownIt
        except ImportError as error:
            raise PreparationError("Declared markdown-it-py converter unavailable; no fallback parser or install was attempted") from error
        body = MarkdownIt("commonmark", {"html": False}).enable("table").render(text)
        converter = {"name": "markdown-it-py", "version": importlib.metadata.version("markdown-it-py")}
        document = f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title></head><body>{body}</body></html>'
    elif input_format == "html":
        document = text
        converter = {"name": "explicit-html", "version": None}
    else:
        raise PreparationError("Choose explicit html or markdown input")
    head = DocumentHead(document)
    if len(head.head_ends) != 1:
        raise PreparationError("HTML needs one explicit closing head; source was not rewritten")
    document_title = title or "".join(head.title).strip()
    size = "" if paper == "custom" else f"size: {'A4' if paper == 'a4' else 'letter'} {orientation};"
    margins = []
    for slot, key in (("top-center", "header"), ("bottom-center", "footer")):
        if key in headers:
            content = _margin_content(headers[key], document_title, date_text or date.today().isoformat())
            margins.append(f"@{slot}{{content:{content};font:9pt Arial,sans-serif;color:#222}}")
    css = (
        f"@page{{{size}margin:18mm;{''.join(margins)}}}\n"
        "@media print{body{margin:0;color:#111;background:#fff;font:11pt/1.45 Arial,sans-serif}"
        "h1,h2,h3{break-after:avoid}p{orphans:3;widows:3}"
        "table{border-collapse:collapse;width:100%}thead{display:table-header-group}"
        "tr{break-inside:avoid}th,td{border:1px solid #555;padding:5pt;text-align:left;vertical-align:top}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere;font:9pt/1.4 monospace}"
        "code{font-family:monospace}img{max-width:100%}a{overflow-wrap:anywhere}}\n"
        + print_css
    )
    if no_background:
        css += "\n@media print{*{background:none!important;box-shadow:none!important}}"
    insertion = f'\n<style data-lintel-pdf="print">\n{css}\n</style>\n'
    position = head.head_ends[0]
    output = document[:position] + insertion + document[position:]
    return output, {
        "converter": converter, "paper": paper, "orientation": orientation,
        "header_footer": headers, "no_background": no_background,
        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "html_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "source_retention": "HTML content preserved with print CSS inserted; Markdown uses the declared converter.",
        "rendered": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True, help="New owned HTML path, never the final PDF")
    parser.add_argument("--format", choices=("a4", "letter", "custom"), default="a4")
    parser.add_argument("--orientation", choices=("portrait", "landscape"), default="portrait")
    parser.add_argument("--header-footer")
    parser.add_argument("--print-css")
    parser.add_argument("--no-background", action="store_true")
    args = parser.parse_args()
    try:
        root = checked_root(args.root)
        source_name, output_name = selector_path(args.input), selector_path(args.out)
        data, _ = read_owned(root, source_name, max_bytes=16 * 1024 * 1024)
        suffix = Path(source_name).suffix.lower()
        if suffix not in (".html", ".htm", ".md", ".markdown"):
            raise PreparationError("Supported source suffixes: .html, .htm, .md, .markdown")
        css = read_owned(root, selector_path(args.print_css), max_bytes=1024 * 1024)[0].decode("utf-8") if args.print_css else ""
        headers = parse_manifest(read_owned(root, selector_path(args.header_footer), max_bytes=65536)[0].decode("utf-8")) if args.header_footer else {}
        output, metadata = prepare_document(
            data.decode("utf-8"), input_format="html" if suffix in (".html", ".htm") else "markdown",
            paper=args.format, orientation=args.orientation, header_footer=headers, print_css=css,
            no_background=args.no_background, title=Path(source_name).stem if suffix in (".md", ".markdown") else "",
        )
        if Path(output_name).suffix.lower() not in (".html", ".htm"):
            raise PreparationError("Prepared output must be HTML, not a renamed PDF")
        atomic_write(root, output_name, output.encode("utf-8"), expected=None, check_expected=True)
        print(json.dumps({"status": "prepared", "input": source_name, "output": output_name, **metadata}, ensure_ascii=True))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "error", "reason": str(error), "rendered": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
