#!/usr/bin/env bash
# Install Orbit Admin like a real app: Almasix + local Orbit + local Conduit.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"          # examples/orbit-admin
REPO="$(cd "$ROOT/../.." && pwd)"             # almasix-orbit
ALMASIX="$(cd "$REPO/../almasix" && pwd)"     # sibling Projects/almasix
CONDUIT="$(cd "$REPO/../almasix-conduit" && pwd)"

if [[ ! -f "$ALMASIX/pyproject.toml" ]]; then
  echo "error: expected Almasix checkout at $ALMASIX" >&2
  exit 1
fi
if [[ ! -f "$CONDUIT/pyproject.toml" ]]; then
  echo "error: expected Almasix Conduit checkout at $CONDUIT" >&2
  exit 1
fi
if [[ ! -f "$REPO/packages/combined/pyproject.toml" ]]; then
  echo "error: missing combined Orbit package at $REPO/packages/combined" >&2
  exit 1
fi

# PyCharm (and friends) resolve ``almasix`` to the framework package and do not
# follow pkgutil.extend_path. Symlink orbit into that tree so ``almasix.orbit``
# is a real subdirectory for the IDE. (gitignored in the Almasix checkout.)
ln -sfn "$REPO/packages/combined/src/almasix/orbit" "$ALMASIX/src/almasix/orbit"
if ! grep -q '^src/almasix/orbit$' "$ALMASIX/.gitignore" 2>/dev/null; then
  printf '\n# Local Orbit checkout (symlink for IDE / editable apps)\nsrc/almasix/orbit\n' \
    >> "$ALMASIX/.gitignore"
fi

cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e "${ALMASIX}[conduit]"
# Prefer local Conduit over the PyPI wheel pulled by almasix[conduit].
pip install -e "$CONDUIT"
pip install -e "$REPO/packages/combined"
pip install -e .
echo "OK — run: source .venv/bin/activate && smith serve"
echo "PyCharm: use this project's .venv, then File → Invalidate Caches if imports stay red."
