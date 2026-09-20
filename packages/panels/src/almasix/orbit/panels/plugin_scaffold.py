"""Scaffold a publishable third-party Orbit plugin and marketplace YAML stubs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

MARKETPLACE_CATEGORIES = frozenset(
    {
        "form-field",
        "form-layout",
        "table-column",
        "table-filter",
        "infolist-entry",
        "action",
        "widget",
        "theme",
        "panel-kit",
        "authentication",
        "integration",
        "localization",
        "developer-tool",
    }
)

RESERVED_PLUGIN_SLUGS = frozenset(
    {
        "authors",
        "categories",
        "develop",
        "feed",
        "get-listed",
        "guidelines",
        "overview",
        "paid",
        "paid-vs-free",
        "using",
    }
)

_SLUG = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$")
_CAMEL = re.compile(r"([a-z0-9])([A-Z])")
_ACRONYM = re.compile(r"([A-Z]+)([A-Z][a-z])")


class PluginScaffoldError(ValueError):
    """Invalid name, category, or destination for a plugin scaffold."""


@dataclass(frozen=True)
class PluginSpec:
    slug: str
    package: str
    module: str
    class_name: str
    plugin_id: str
    display_name: str
    author: str
    vendor: str
    category: str
    orbit_line: str
    paid: bool
    summary: str


def kebab(name: str) -> str:
    text = str(name or "").strip().replace("_", "-").replace(".", "-").replace("/", "-")
    text = _ACRONYM.sub(r"\1-\2", text)
    text = _CAMEL.sub(r"\1-\2", text)
    slug = re.sub(r"-+", "-", text.lower()).strip("-")
    return slug


def studly(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in kebab(name).split("-") if part)


def title_words(name: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in kebab(name).split("-") if part)


def _require_slug(value: str, *, label: str) -> str:
    slug = kebab(value)
    if not slug or not _SLUG.match(slug):
        raise PluginScaffoldError(f"{label} must be a kebab-case slug, got {value!r}")
    return slug


def parse_plugin_spec(
    name: str,
    *,
    author: str = "",
    vendor: str = "",
    package: str = "",
    category: str = "developer-tool",
    paid: bool = False,
    orbit_line: str = "0.4",
) -> PluginSpec:
    raw = kebab(str(name or "").removesuffix("-plugin"))
    if not raw:
        raise PluginScaffoldError("name is required")
    if raw.startswith("almasix-orbit"):
        raise PluginScaffoldError(
            "the almasix-orbit-* prefix is reserved for official Orbit packages"
        )
    raw = _require_slug(raw, label="name")

    vendor_slug = kebab(vendor) if vendor else ""
    author_slug = kebab(author) if author else ""
    if not vendor_slug:
        vendor_slug = raw.split("-", 1)[0] if "-" in raw else author_slug or "acme"
    vendor_slug = _require_slug(vendor_slug, label="vendor")
    if vendor_slug == "almasix":
        raise PluginScaffoldError("vendor 'almasix' is reserved for official packages")

    author_slug = _require_slug(author_slug or vendor_slug, label="author")

    if package:
        dist = _require_slug(package, label="package")
    elif "-orbit-" in raw:
        dist = raw
    else:
        feature = raw.removeprefix(f"{vendor_slug}-") or raw
        dist = f"{vendor_slug}-orbit-{feature}"
    dist = _require_slug(dist, label="package")
    if dist.startswith("almasix-orbit"):
        raise PluginScaffoldError(
            "the almasix-orbit-* prefix is reserved for official Orbit packages"
        )

    parts = dist.split("-")
    if len(parts) >= 3 and parts[1] == "orbit":
        slug = f"{parts[0]}-{'-'.join(parts[2:])}"
        feature = "-".join(parts[2:])
    else:
        slug = dist
        feature = dist.removeprefix(f"{vendor_slug}-") or dist
    slug = _require_slug(slug, label="slug")
    if slug in RESERVED_PLUGIN_SLUGS:
        raise PluginScaffoldError(f"{slug!r} is reserved for marketplace routes")

    category_slug = kebab(category) or "developer-tool"
    if category_slug not in MARKETPLACE_CATEGORIES:
        allowed = ", ".join(sorted(MARKETPLACE_CATEGORIES))
        raise PluginScaffoldError(f"unknown category {category!r}; use one of: {allowed}")

    class_name = f"{studly(feature)}Plugin"
    display = title_words(feature)
    return PluginSpec(
        slug=slug,
        package=dist,
        module=dist.replace("-", "_"),
        class_name=class_name,
        plugin_id=slug,
        display_name=display,
        author=author_slug,
        vendor=vendor_slug,
        category=category_slug,
        orbit_line=str(orbit_line or "0.4"),
        paid=bool(paid),
        summary=f"{display} for Orbit panels.",
    )


def resolve_root(path: str | Path, spec: PluginSpec, *, listing_only: bool) -> Path:
    dest = Path(path).expanduser().resolve()
    if listing_only:
        return dest
    if dest.name in {spec.package, spec.slug, spec.module}:
        return dest
    return dest / spec.package


def _plugin_py(spec: PluginSpec) -> str:
    return f'''"""Orbit plugin: {spec.display_name}."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.hooks import Plugin


class {spec.class_name}(Plugin):
    """Passive plugin — the host app calls ``panel.plugin({spec.class_name}())``."""

    def __init__(self) -> None:
        super().__init__("{spec.plugin_id}")

    def register(self, panel: Any) -> None:
        """Mutate panel config before routes mount. Keep this free of I/O."""
        return None

    def boot(self, panel: Any) -> None:
        """Side effects at mount — render hooks, routes, discovery."""
        panel.render_hook(
            "panels::styles.after",
            lambda **_ctx: "<!-- {spec.plugin_id} booted -->\\n",
        )
'''


def _init_py(spec: PluginSpec) -> str:
    return f'''"""Publishable Orbit plugin package: {spec.package}."""

from {spec.module}.plugin import {spec.class_name}

__all__ = ["{spec.class_name}"]
'''


def _pyproject(spec: PluginSpec) -> str:
    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{spec.package}"
version = "0.1.0"
description = "{spec.summary.replace('"', "'")}"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "almasix-orbit>={spec.orbit_line}.0",
]

[project.urls]
Documentation = "https://orbit.almasix.com/panels/plugins/"

[tool.hatch.build.targets.wheel]
packages = ["src/{spec.module}"]
'''


def _readme(spec: PluginSpec) -> str:
    vcs = f"git+https://github.com/{spec.author}/{spec.package}.git"
    price = "paid" if spec.paid else "free"
    return f'''# {spec.display_name}

Orbit plugin (`{spec.plugin_id}`). Register it on a panel — Orbit never auto-discovers plugins.

## Install

```bash
pip install {spec.package}
# or, GitHub-only:
pip install "{vcs}@v0.1.0"
```

```python
from {spec.module} import {spec.class_name}

panel.plugin({spec.class_name}())
```

## Marketplace listing

This package ships draft YAML under `marketplace/`. Copy those files into the
Orbit repository (`docs/src/data/marketplace/`) when you are ready to list it
({price}). See https://orbit.almasix.com/plugins/get-listed/

Do **not** ship an `almasix/__init__.py` in this wheel.
'''


def _license() -> str:
    return """MIT License

Copyright (c) 2026 the plugin author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def _gitignore() -> str:
    return """__pycache__/
*.py[cod]
.venv/
dist/
*.egg-info/
"""


def _test_py(spec: PluginSpec) -> str:
    return f'''"""Smoke test: register then boot."""

from __future__ import annotations

from almasix.orbit import Panel
from {spec.module} import {spec.class_name}


def test_register_then_boot() -> None:
    panel = Panel.make("admin").path("admin")
    plugin = {spec.class_name}()
    plugin.register(panel)
    plugin.boot(panel)
    assert plugin.get_id() == "{spec.plugin_id}"
'''


def _plugin_yaml(spec: PluginSpec, *, published_at: str) -> str:
    repo = f"https://github.com/{spec.author}/{spec.package}"
    if spec.paid:
        price_block = """price:
  amount: 29
  currency: USD
checkout_url: https://example.com/checkout  # replace with a real purchase URL
"""
    else:
        price_block = f"""price: free
package: {spec.package}
repository: {repo}
"""
    return f"""# Draft marketplace listing. Copy to the Orbit repo:
#   docs/src/data/marketplace/plugins/{spec.slug}.yaml
# Fill in summary, description, images, then set status: published.
# Field reference: https://orbit.almasix.com/plugins/get-listed/

name: {spec.display_name}
slug: {spec.slug}
summary: {spec.summary}
description: |
  ## What it does

  Replace this with a few paragraphs of markdown. Headings, links, lists,
  and code fences all render on the listing page.

  ## Setup

  ```bash
  pip install {spec.package}
  ```

  ```python
  panel.plugin({spec.class_name}())
  ```
author: {spec.author}
categories:
  - {spec.category}
orbit_versions:
  - "{spec.orbit_line}"
{price_block}# thumbnail: /plugins/{spec.slug}/thumbnail.jpg
# screenshots:
#   - src: /plugins/{spec.slug}/screenshot.png
#     alt: Describe what the screenshot shows
features:
  dark_mode: false
license: MIT
keywords: [{spec.slug}]
status: draft
published_at: {published_at}
"""


def _author_yaml(spec: PluginSpec) -> str:
    return f"""# Draft author profile. Copy to the Orbit repo:
#   docs/src/data/marketplace/authors/{spec.author}.yaml
# Skip this file if you already have an author listing.

name: {title_words(spec.author)}
slug: {spec.author}
bio: One or two sentences about you or your company, shown on your author page.
# avatar: /plugins/authors/{spec.author}.jpg
# website: https://example.com
# github: {spec.author}
# sponsor_url: https://github.com/sponsors/{spec.author}
"""


def planned_files(root: Path, spec: PluginSpec, *, listing_only: bool, no_listing: bool) -> dict[str, str]:
    published = date.today().isoformat()
    files: dict[str, str] = {}
    if not listing_only:
        files.update(
            {
                "pyproject.toml": _pyproject(spec),
                "README.md": _readme(spec),
                "LICENSE": _license(),
                ".gitignore": _gitignore(),
                f"src/{spec.module}/__init__.py": _init_py(spec),
                f"src/{spec.module}/plugin.py": _plugin_py(spec),
                "tests/test_plugin.py": _test_py(spec),
            }
        )
    if not no_listing:
        files[f"marketplace/{spec.slug}.yaml"] = _plugin_yaml(spec, published_at=published)
        files[f"marketplace/{spec.author}.yaml"] = _author_yaml(spec)
    return {str(root / rel): body for rel, body in files.items()}


def write_scaffold(
    spec: PluginSpec,
    *,
    path: str | Path,
    listing_only: bool = False,
    no_listing: bool = False,
    force: bool = False,
) -> list[Path]:
    if listing_only and no_listing:
        raise PluginScaffoldError("cannot combine listing-only with no-listing")
    root = resolve_root(path, spec, listing_only=listing_only)
    planned = planned_files(root, spec, listing_only=listing_only, no_listing=no_listing)
    existing = [Path(p) for p in planned if Path(p).exists()]
    if existing and not force:
        raise PluginScaffoldError(f"already exists: {existing[0]} (pass --force to overwrite)")
    written: list[Path] = []
    for target, body in planned.items():
        out = Path(target)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        written.append(out)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m almasix.orbit",
        description="Orbit developer tools",
    )
    groups = parser.add_subparsers(dest="group", required=True)
    plugin = groups.add_parser("plugin", help="Third-party plugin helpers")
    actions = plugin.add_subparsers(dest="action", required=True)
    new = actions.add_parser(
        "new",
        help="Scaffold a publishable plugin package and marketplace YAML stubs",
    )
    new.add_argument("name", nargs="?", help="Plugin name (AuditLog or acme-orbit-audit-log)")
    new.add_argument("--author", default="", help="Author slug for the listing YAML")
    new.add_argument("--vendor", default="", help="Vendor prefix for the PyPI name")
    new.add_argument("--package", default="", help="PyPI package name")
    new.add_argument(
        "--category",
        default="developer-tool",
        help="Marketplace category (default: developer-tool)",
    )
    new.add_argument(
        "--path",
        default=".",
        help="Directory to write into (defaults to the current working directory)",
    )
    new.add_argument("--paid", action="store_true", help="Paid listing stub")
    exclusive = new.add_mutually_exclusive_group()
    exclusive.add_argument(
        "--listing-only",
        action="store_true",
        dest="listing_only",
        help="Only write marketplace YAML stubs",
    )
    exclusive.add_argument(
        "--no-listing",
        action="store_true",
        dest="no_listing",
        help="Skip marketplace YAML",
    )
    new.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser


def run_new(args: argparse.Namespace, *, stdout: Any = None) -> int:
    from sys import stdout as default_out

    out = stdout or default_out
    name = str(getattr(args, "name", None) or "").strip()
    if not name:
        out.write("name is required\n")
        return 2
    try:
        spec = parse_plugin_spec(
            name,
            author=str(args.author or ""),
            vendor=str(args.vendor or ""),
            package=str(args.package or ""),
            category=str(args.category or "developer-tool"),
            paid=bool(args.paid),
        )
        written = write_scaffold(
            spec,
            path=str(args.path or "."),
            listing_only=bool(args.listing_only),
            no_listing=bool(args.no_listing),
            force=bool(args.force),
        )
    except PluginScaffoldError as exc:
        out.write(f"{exc}\n")
        return 1
    root = resolve_root(str(args.path or "."), spec, listing_only=bool(args.listing_only))
    out.write(f"plugin scaffold → {root}\n")
    for path in written:
        out.write(f"  {path}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 0 if code in (None, 0) else int(code)
    return run_new(args)
