from __future__ import annotations

from collections import defaultdict

import fitz


def extract_pdf_structure(pdf_bytes: bytes) -> dict:
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    headings: list[dict] = []
    body_chunks: list[str] = []
    heading_buckets: dict[str, list[str]] = defaultdict(list)
    current_heading = "Overview"

    for page in document:
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if "lines" not in block:
                continue
            line_text = " ".join(
                span["text"].strip()
                for line in block["lines"]
                for span in line["spans"]
                if span["text"].strip()
            ).strip()
            if not line_text:
                continue

            max_size = max(
                (span["size"] for line in block["lines"] for span in line["spans"]),
                default=0,
            )
            is_heading = max_size >= 15 or (
                len(line_text.split()) <= 8 and line_text == line_text.title()
            )

            if is_heading:
                current_heading = line_text
                headings.append({"heading": current_heading, "points": []})
            else:
                body_chunks.append(line_text)
                heading_buckets[current_heading].append(line_text)

    summary = []
    seen = set()
    for heading in headings[:12]:
        heading_title = heading["heading"]
        if heading_title in seen:
            continue
        seen.add(heading_title)
        points = heading_buckets.get(heading_title, [])[:4]
        summary.append({"heading": heading_title, "points": points})

    if not summary:
        summary = [{"heading": "Overview", "points": body_chunks[:8]}]

    full_text = "\n".join(body_chunks)
    return {
        "summary": summary,
        "excerpt": full_text[:12000],
    }

