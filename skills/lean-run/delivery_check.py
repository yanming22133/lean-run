#!/usr/bin/env python3
"""Fast mechanical delivery check for PDF deliverables.

This is a gate, not a replacement for visual inspection. It catches the
common rework causes: missing sections, missing figures, leftover
placeholders, page-count issues, and absent key results.
"""

import argparse
import json
import os
import re
import sys


def load_text(path):
    texts = []
    pages = 0
    images = 0
    try:
        import pymupdf

        doc = pymupdf.open(path)
        pages = doc.page_count
        images = sum(len(page.get_images(full=True)) for page in doc)
        texts.append("\n".join(page.get_text() for page in doc))
        doc.close()
    except Exception:
        pass
    if not texts:
        try:
            import pypdf

            reader = pypdf.PdfReader(path)
            pages = len(reader.pages)
            texts.append("\n".join((p.extract_text() or "") for p in reader.pages))
        except Exception:
            pass
    text = max(texts, key=len) if texts else ""
    return text, pages, images


def norm(text):
    return re.sub(r"\s+", "", text)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Check a PDF against a delivery checklist.")
    ap.add_argument("pdf")
    ap.add_argument("--min-pages", type=int, default=1)
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--heading", action="append", default=[])
    ap.add_argument("--text", action="append", default=[])
    ap.add_argument("--forbid", action="append", default=[])
    ap.add_argument("--min-images", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        sys.exit(f"PDF not found: {args.pdf}")

    text, pages, images = load_text(args.pdf)
    ntext = norm(text)

    forbids = args.forbid or ["________", "TODO", "TBD", "XXX"]
    checks = []
    checks.append(("pages", pages >= args.min_pages, f"{pages} >= {args.min_pages}"))
    if args.max_pages:
        checks.append(("page_limit", pages <= args.max_pages, f"{pages} <= {args.max_pages}"))
    checks.append(("images", images >= args.min_images, f"{images} >= {args.min_images}"))
    checks.append(("text_extractable", bool(text.strip()), f"{len(text)} chars"))

    for h in args.heading:
        checks.append((f"heading:{h}", norm(h) in ntext, "found" if norm(h) in ntext else "missing"))
    for t in args.text:
        checks.append((f"text:{t}", norm(t) in ntext, "found" if norm(t) in ntext else "missing"))
    for f in forbids:
        present = norm(f) in ntext
        checks.append((f"forbid:{f}", not present, "absent" if not present else "present"))

    passed = all(ok for _, ok, _ in checks)
    if args.json:
        print(json.dumps({
            "pdf": args.pdf,
            "passed": passed,
            "pages": pages,
            "images": images,
            "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Delivery check: {args.pdf}")
        print(f"pages={pages} images={images}")
        for name, ok, detail in checks:
            print(f"  {'PASS' if ok else 'FAIL'}  {name}  ({detail})")
        print("RESULT:", "PASS" if passed else "FAIL")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
