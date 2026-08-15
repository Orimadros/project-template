#!/usr/bin/env python3
"""Convert a native-text PDF to Markdown with Firecrawl pdf-inspector.

Inputs:
    A PDF path and, optionally, a Markdown output path.
Outputs:
    A UTF-8 Markdown file. The command reports the PDF classification and any
    pages that need OCR on stderr so callers do not mistake a partial extract
    for a complete transcription.

This is intentionally a project utility rather than a data-pipeline stage. It
gives agents one reproducible PDF-reading command backed by the version pinned
in ``uv.lock``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown with Firecrawl pdf-inspector."
    )
    parser.add_argument("pdf", type=Path, help="source PDF to inspect and convert")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Markdown output path (defaults to the PDF path with a .md suffix)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    pdf_path = args.pdf
    output_path = args.output or pdf_path.with_suffix(".md")

    if not pdf_path.is_file():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    try:
        import pdf_inspector
    except ImportError:
        print(
            "Error: pdf-inspector is not installed. Run `make setup` from the "
            "project root, then retry.",
            file=sys.stderr,
        )
        return 1

    try:
        result = pdf_inspector.process_pdf(str(pdf_path))
    except Exception as error:
        print(f"Error: pdf-inspector could not process {pdf_path}: {error}", file=sys.stderr)
        return 1

    pdf_type = str(getattr(result, "pdf_type", "unknown"))
    page_count = getattr(result, "page_count", "unknown")
    pages_needing_ocr = list(getattr(result, "pages_needing_ocr", []) or [])
    has_encoding_issues = bool(getattr(result, "has_encoding_issues", False))
    markdown = getattr(result, "markdown", None)

    print(
        f"pdf-inspector: type={pdf_type}; pages={page_count}; "
        f"pages_needing_ocr={pages_needing_ocr or 'none'}",
        file=sys.stderr,
    )

    if pdf_type in {"scanned", "image_based"} or not markdown:
        print(
            "No Markdown was written because this PDF needs OCR. Inspect the "
            "original PDF or page images for the needed material, or obtain an "
            "authorized OCR/text version before relying on its contents.",
            file=sys.stderr,
        )
        return 2

    if not output_path.parent.is_dir():
        print(f"Error: output directory does not exist: {output_path.parent}", file=sys.stderr)
        return 1

    output_path.write_text(markdown, encoding="utf-8")
    print(f"Markdown written to: {output_path}", file=sys.stderr)

    if pdf_type == "mixed" or pages_needing_ocr or has_encoding_issues:
        warning = (
            "Warning: this Markdown may be incomplete. Visually inspect the "
            "original PDF or page images"
        )
        if pages_needing_ocr:
            warning += f" for OCR-needed pages {pages_needing_ocr}"
        if has_encoding_issues:
            warning += " because pdf-inspector detected font-encoding issues"
        print(f"{warning}.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
