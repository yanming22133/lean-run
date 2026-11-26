#!/usr/bin/env python3
"""Extract a delivery checklist from a DOCX template.

Usage:
  python template_spec.py answer_template.docx
  python template_spec.py answer_template.docx --json

The output is a starting point: choose the headings/placeholders that matter,
then pass them to delivery_check.py.
"""

import argparse
import json
import os
import re
import sys


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Extract headings/placeholders/images from a DOCX template.")
    ap.add_argument("docx")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.docx):
        sys.exit(f"DOCX not found: {args.docx}")

    try:
        from docx import Document
    except ImportError:
        sys.exit("python-docx is required: python -m pip install python-docx")

    doc = Document(args.docx)
    paragraphs = []
    headings = []
    placeholders = []
    identity_fields = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        bold = any(r.bold for r in p.runs if r.text.strip())
        sizes = [r.font.size.pt for r in p.runs if r.font.size is not None]
        size = max(sizes) if sizes else None
        paragraphs.append({"text": text, "bold": bold, "size": size})
        if bold and len(text) <= 40:
            headings.append(text)
        if re.search(r"_{3,}", text):
            placeholders.append(text)
        if any(k in text for k in ("姓名", "学校", "日期", "签名")):
            identity_fields.append(text)

    images = len(doc.inline_shapes)
    section = doc.sections[0]
    page = {
        "width_in": round(section.page_width.inches, 2),
        "height_in": round(section.page_height.inches, 2),
        "left_margin_in": round(section.left_margin.inches, 2),
        "right_margin_in": round(section.right_margin.inches, 2),
    }

    spec = {
        "docx": args.docx,
        "page": page,
        "images": images,
        "headings": headings,
        "placeholders": placeholders,
        "identity_fields": identity_fields,
        "paragraphs": paragraphs,
    }

    if args.json:
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return

    print(f"Template: {args.docx}")
    print(f"Page: {page['width_in']} x {page['height_in']} in, images={images}")
    print("Headings (bold, short):")
    for h in headings:
        print(f"  - {h}")
    print("Blank placeholders:")
    for p in placeholders:
        print(f"  - {p}")
    print("Identity fields (verify filled; do not forbid the labels):")
    for p in identity_fields:
        print(f"  - {p}")
    print("\nSuggested check (edit as needed):")
    heading_args = " ".join(f'--heading "{h}"' for h in headings)
    forbid_args = " ".join(f'--forbid "{p}"' for p in placeholders)
    identity_args = " ".join(f'--text "{p}"' for p in identity_fields)
    print(f'python delivery_check.py answer.pdf --min-pages 2 --min-images {images} {heading_args} {identity_args} {forbid_args}')


if __name__ == "__main__":
    main()
