#!/usr/bin/env python3
"""Generate Filament-style Forms/Schemas docs from shot-catalog.json.

Structure per page:
  ## Introduction  (rich prose)
  ## {Variant heading}
     blurb
     code fence
     screenshot pair (light/dark — theme CSS hides the inactive one)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path(__file__).resolve().parent / "shot-catalog.json"
DOCS = ROOT / "src" / "content" / "docs"


def fold_fluent_code(code: str) -> str:
    """Stack fluent ``.method()`` calls vertically (Filament-style).

    Shows the exact chain users paste into ``.schema([...])`` / ``.columns([...])`` —
    no wrapping parentheses. Trailing ``#`` comments stay on the last line.
    Nested calls inside ``()`` / ``[]`` are left alone.
    """
    code = code.strip()
    if not code or "\n" in code:
        return code

    comment = ""
    if "  #" in code:
        code, _, rest = code.partition("  #")
        comment = "  #" + rest
        code = code.rstrip()

    # Keep an existing assignment / return on the first line of the chain.
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
                i += 1
                continue
            continue
        buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf))

    if len(parts) <= 1:
        return prefix + code + comment

    # Filament-style: stack methods — paste into schema/columns lists as-is.
    body = parts[0] + "".join("\n    " + part for part in parts[1:])
    if prefix:
        # Assignment needs an open paren for a valid multi-line RHS in Python.
        # Prefer dropping the assignment so the snippet matches field definitions.
        return body + comment
    return body + comment


def unwrap_paren_expression(body: str) -> str:
    """Turn ``(\\n    expr\\n)`` / ``name = (\\n    expr\\n)`` into a Filament-style chain."""

    def restack(inner: str) -> str:
        lines = []
        for line in inner.split("\n"):
            lines.append(line[4:] if line.startswith("    ") else line)
        if not lines:
            return inner
        out = [lines[0]]
        for line in lines[1:]:
            # Re-indent chained .method() lines that sat at the same indent inside ().
            if line.startswith("."):
                out.append("    " + line)
            else:
                out.append(line)
        return "\n".join(out)

    text = body.strip("\n")
    # Optional trailing comment after closing paren: )\n or )  # note
    assign_m = re.match(
        r"^([A-Za-z_][\w.]*\s*=\s*)\(\n([\s\S]*?)\n\)(\s*#.*)?$",
        text,
    )
    if assign_m:
        return restack(assign_m.group(2)) + (assign_m.group(3) or "")
    bare_m = re.match(r"^\(\n([\s\S]*?)\n\)(\s*#.*)?$", text)
    if bare_m:
        return restack(bare_m.group(1)) + (bare_m.group(2) or "")
    return body


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
            "Each variation below includes a short explanation, the fluent API "
            "to paste into your schema, and a screenshot of the rendered control."
        )
        parts.append("")

    for variant in variants:
        shot_id = variant["id"]
        heading = variant["heading"]
        blurb = variant.get("blurb") or ""
        code = variant.get("code") or ""
        parts.append(f"## {heading}")
        parts.append("")
        # Explanation + code first, then screenshot
        if blurb:
            parts.append(blurb)
            parts.append("")
        if code:
            fence = fold_fluent_code(code)
            parts.append("```python")
            parts.append(fence)
            parts.append("```")
            parts.append("")
        parts.append(preview_pair(shot_id, heading))

    parts.append(
        "Closures work on `.label()`, `.helper_text()`, `.placeholder()`, "
        "`.visible()`, `.disabled()`, and `.required()` where applicable — "
        "see [Form closures](/forms/closures/)."
    )
    parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def fold_python_fences_in_markdown(text: str) -> str:
    """Fold single-line fluent fences; unwrap earlier paren-wrapped chains."""

    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        stripped = body.strip("\n")
        unwrapped = unwrap_paren_expression(stripped)
        if "\n" not in unwrapped:
            folded = fold_fluent_code(unwrapped)
            if folded == stripped:
                return match.group(0)
            return "```python\n" + folded + "\n```"
        if unwrapped != stripped:
            return "```python\n" + unwrapped + "\n```"
        return match.group(0)

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
