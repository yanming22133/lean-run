#!/usr/bin/env python3
"""Fast mechanical delivery check for PDF deliverables.

This is a gate, not a replacement for visual inspection. It catches the
common rework causes: missing/ordered sections, missing figures, leftover
placeholders, page-count issues, and absent key results.
"""

import argparse
import json
import os
import re
import sys

DEFAULT_FORBID = ["________", "TODO", "TBD", "XXX"]


def load_pdf(path):
    """Return (text, pages, unique_image_xrefs, backend)."""
    try:
        import pymupdf

        doc = pymupdf.open(path)
        pages = doc.page_count
        xrefs = set()
        for page in doc:
            for img in page.get_images(full=True):
                xrefs.add(img[0])
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text, pages, len(xrefs), "pymupdf"
    except ImportError:
        pass
    except Exception as exc:
        raise RuntimeError(f"PyMuPDF failed to read the PDF: {exc}") from exc

    try:
        import pypdf

        reader = pypdf.PdfReader(path)
        pages = len(reader.pages)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        return text, pages, None, "pypdf"
    except ImportError as exc:
        raise RuntimeError(
            "No PDF backend available. Install pymupdf (recommended) or pypdf."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"pypdf failed to read the PDF: {exc}") from exc


def norm(text):
    return re.sub(r"\s+", "", text)


def strip_number_prefix(line):
    """Remove common heading numbering: 一、, 1., 1.2, (1), 第一章."""
    s = line.strip()
    s = re.sub(r"^第[一二三四五六七八九十百]+[章节部分]\s*", "", s)
    s = re.sub(r"^[一二三四五六七八九十百]+[、.．]\s*", "", s)
    s = re.sub(r"^\d+(?:\.\d+)*[、.．)]?\s*", "", s)
    s = re.sub(r"^[（(]\d+[）)]\s*", "", s)
    return s.strip()


def line_matches_heading(line, heading):
    h = heading.strip()
    s = strip_number_prefix(line)
    if not s.startswith(h):
        return False
    rest = s[len(h):]
    return not rest or rest[0] in " \t:：、，,。.-—)）]"


def heading_matches(text, heading):
    """Line-start match with a boundary, so Method != Methodology."""
    return any(line_matches_heading(line, heading) for line in text.splitlines())


def text_matches(text, needle):
    """Substring for words; numeric token boundary for numbers."""
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", needle.strip()):
        pattern = r"(?<![\d.])" + re.escape(needle.strip()) + r"(?![\d])"
        return re.search(pattern, text) is not None
    return needle in text


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Check a PDF against a delivery checklist.")
    ap.add_argument("pdf")
    ap.add_argument("--min-pages", type=int, default=1)
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--heading", action="append", default=[],
                    help="Required heading; repeat in document order.")
    ap.add_argument("--text", action="append", default=[],
                    help="Required text/result; repeat as needed.")
    ap.add_argument("--forbid", action="append", default=[],
                    help="Extra forbidden strings; defaults are always included.")
    ap.add_argument("--no-default-forbid", action="store_true",
                    help="Do not include ________/TODO/TBD/XXX defaults.")
    ap.add_argument("--min-images", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        sys.exit(f"PDF not found: {args.pdf}")

    try:
        text, pages, images, backend = load_pdf(args.pdf)
    except RuntimeError as exc:
        sys.exit(str(exc))

    if images is None and args.min_images > 0:
        sys.exit(
            "Image counting requires PyMuPDF. Install it with: "
            "python -m pip install pymupdf"
        )

    ntext = norm(text)
    if "\ufffd" in text:
        # U+FFFD usually means a missing font / broken text extraction.
        pass  # reported as a check below

    forbids = [] if args.no_default_forbid else list(DEFAULT_FORBID)
    forbids += args.forbid
    forbids = list(dict.fromkeys(forbids))

    checks = []
    checks.append(("pages", pages >= args.min_pages, f"{pages} >= {args.min_pages}"))
    if args.max_pages:
        checks.append(("page_limit", pages <= args.max_pages, f"{pages} <= {args.max_pages}"))
    if args.min_images:
        checks.append(("images", images >= args.min_images, f"{images} >= {args.min_images}"))
    checks.append(("text_extractable", bool(text.strip()), f"{len(text)} chars"))
    checks.append(("no_replacement_char", "\ufffd" not in text,
                   "no U+FFFD" if "\ufffd" not in text else "U+FFFD found"))

    positions = []
    for h in args.heading:
        found = heading_matches(text, h)
        checks.append((f"heading:{h}", found, "found" if found else "missing"))
        if found:
            lines = [line.strip() for line in text.splitlines()]
            start = positions[-1] + 1 if positions else 0
            pos = next((i for i in range(start, len(lines))
                        if line_matches_heading(lines[i], h)), None)
            positions.append(pos if pos is not None else -1)

    if positions and all(p >= 0 for p in positions):
        ordered = all(a < b for a, b in zip(positions, positions[1:]))
        checks.append(("heading_order", ordered, "in order" if ordered else "out of order"))

    for t in args.text:
        found = text_matches(text, t)
        checks.append((f"text:{t}", found, "found" if found else "missing"))

    for f in forbids:
        present = norm(f) in ntext
        checks.append((f"forbid:{f}", not present, "absent" if not present else "present"))

    passed = all(ok for _, ok, _ in checks)
    if args.json:
        print(json.dumps({
            "pdf": args.pdf,
            "backend": backend,
            "passed": passed,
            "pages": pages,
            "images": images,
            "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Delivery check: {args.pdf}")
        print(f"backend={backend} pages={pages} images={images}")
        for name, ok, detail in checks:
            print(f"  {'PASS' if ok else 'FAIL'}  {name}  ({detail})")
        print("RESULT:", "PASS" if passed else "FAIL")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
