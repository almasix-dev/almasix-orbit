#!/usr/bin/env bash
# Install Orbit Demo from production PyPI releases (same as Docker / Render).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e .
echo "OK — PyPI almasix / almasix-orbit / almasix-conduit installed."
python - <<'PY'
from importlib.metadata import version

for name in ("almasix", "almasix-orbit", "almasix-conduit"):
    print(f"  {name} {version(name)}")
PY
echo "Next: source .venv/bin/activate && smith migrate --seed && smith serve"
echo "Demo login: demo@orbit.test / secret"
