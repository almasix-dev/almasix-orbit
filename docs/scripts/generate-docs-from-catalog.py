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
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path(__file__).resolve().parent / "shot-catalog.json"
DOCS = ROOT / "src" / "content" / "docs"


def fold_fluent_code(code: str) -> str:
    """Stack fluent ``.method()`` calls vertically so snippets don't need horizontal scroll.

    ``Class.make(...)`` stays on the first line; each subsequent chained call is indented.
    Trailing ``#`` comments are preserved on the last line. Nested calls inside ``()``/``[]``
    are left alone so only top-level chain links break.

    Assignments like ``x = Foo.make().bar()`` become ``x = (\\n    Foo.make()\\n    .bar()\\n)``.
    Incomplete lines (unbalanced brackets) are left unchanged.
    """
    code = code.strip()
    if not code or "\n" in code:
        return code

    comment = ""
    if "  #" in code:
        code, _, rest = code.partition("  #")
        comment = "  #" + rest
        code = code.rstrip()

    # Preserve leading assignment / return / yield targets outside the wrap.
    prefix = ""
    assign = re.match(r"^((?:return|yield)\s+|[A-Za-z_][\w.]*\s*=\s*)", code)
    if assign:
        prefix = assign.group(1)
        code = code[assign.end() :]

    def bracket_balance(s: str) -> int:
        depth = 0
        in_str: str | None = None
        escape = False
        for ch in s:
            if in_str is not None:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == in_str:
                    in_str = None
                continue
            if ch in ("'", '"'):
                in_str = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(0, depth - 1)
        return depth

    # Don't touch continuation lines or incomplete calls.
    if bracket_balance(code) != 0:
        return prefix + code + comment

    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    in_str: str | None = None
    escape = False
    i = 0
    while i < len(code):
        ch = code[i]
        if in_str is not None:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_str = ch
            buf.append(ch)
            i += 1
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
            i += 1
            continue
        if ch in ")]}":
            depth = max(0, depth - 1)
            buf.append(ch)
            i += 1
            if (
                depth == 0
                and i < len(code)
                and code[i] == "."
                and i + 1 < len(code)
                and (code[i + 1].isalpha() or code[i + 1] == "_")
            ):
                parts.append("".join(buf))
                buf = ["."]
                i += 1  # consume '.'
                continue
            continue
        buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf))

    if len(parts) <= 1:
        return prefix + code + comment

    # Parentheses make vertical fluent chains valid Python (unlike PHP's ->).
    body = parts[0] + "".join("\n    " + part for part in parts[1:])
    return prefix + "(\n    " + body + "\n)" + comment


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
            fence = fold_fluent_code(code)
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


def fold_python_fences_in_markdown(text: str) -> str:
    """Fold single-line fluent fences only — leave multi-line examples untouched."""

    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        stripped = body.strip("\n")
        if "\n" in stripped:
            return match.group(0)
        folded = fold_fluent_code(stripped)
        if folded == stripped:
            return match.group(0)
        return "```python\n" + folded + "\n```"

    return re.sub(r"```python\n(.*?)```", repl, text, flags=re.S)


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    written = 0
    catalog_slugs: set[str] = set()
    for slug, page in catalog.items():
        catalog_slugs.add(slug)
        path = DOCS / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_page(slug, page), encoding="utf-8")
        written += 1
        print(f"wrote {path.relative_to(ROOT)}")

    # Fold fluent chains in non-catalog docs (overviews, tables, etc.)
    extra = 0
    for path in DOCS.rglob("*.md"):
        rel = path.relative_to(DOCS).with_suffix("").as_posix()
        if rel in catalog_slugs:
            continue
        original = path.read_text(encoding="utf-8")
        if "```python" not in original:
            continue
        updated = fold_python_fences_in_markdown(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            extra += 1
            print(f"folded {path.relative_to(ROOT)}")

    print(f"done: {written} catalog pages, {extra} other pages folded")


if __name__ == "__main__":
    main()
