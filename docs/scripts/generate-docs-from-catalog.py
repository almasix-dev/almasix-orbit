#!/usr/bin/env python3
"""Generate Filament-style Forms/Schemas docs from shot-catalog.json.

Structure per page:
  ## Introduction  (rich prose)
  ## {Variant heading}
     screenshot pair (light/dark — theme CSS hides the inactive one)
     blurb
     code fence
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path(__file__).resolve().parent / "shot-catalog.json"
DOCS = ROOT / "src" / "content" / "docs"


def preview_pair(shot_id: str, alt: str) -> str:
    return (
        f"![Orbit {alt} (light)](/examples/light/{shot_id}.png)\n\n"
        f"![Orbit {alt} (dark)](/examples/dark/{shot_id}.png)\n"
    )


def render_page(slug: str, page: dict) -> str:
    title = page["title"]
    intro = page["intro"].strip()
    variants = page.get("variants") or []
    desc = intro.split(".")[0].strip() + "."
    if len(desc) > 160:
        desc = desc[:157] + "…"

    parts: list[str] = [
        "---",
        f"title: {title}",
        f"description: {desc}",
        "---",
        "",
        "## Introduction",
        "",
        intro,
        "",
    ]

    if variants:
        parts.append(
            "The screenshots below show how each variation renders in Orbit. "
            "Each section includes the fluent API used to produce it."
        )
        parts.append("")

    for variant in variants:
        shot_id = variant["id"]
        heading = variant["heading"]
        blurb = variant.get("blurb") or ""
        code = variant.get("code") or ""
        parts.append(f"## {heading}")
        parts.append("")
        # Preview first (Filament-style), then explanation + code
        parts.append(preview_pair(shot_id, heading))
        if blurb:
            parts.append(blurb)
            parts.append("")
        if code:
            fence = code.strip()
            parts.append("```python")
            parts.append(fence)
            parts.append("```")
            parts.append("")

    parts.append(
        "Closures work on `.label()`, `.helper_text()`, `.placeholder()`, "
        "`.visible()`, `.disabled()`, and `.required()` where applicable — "
        "see [Form closures](/forms/closures/)."
    )
    parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    written = 0
    for slug, page in catalog.items():
        # slug like forms/text-input or schemas/section
        path = DOCS / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_page(slug, page), encoding="utf-8")
        written += 1
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"done: {written} pages")


if __name__ == "__main__":
    main()
