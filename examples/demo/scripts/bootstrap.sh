#!/usr/bin/env bash
# Install Orbit Demo from production PyPI packages (no local Orbit / Almasix /
# Conduit editables or monorepo path installs).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"          # examples/demo

cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel

# Demo app editable; framework deps resolve from PyPI via pyproject.toml.
pip install -e .

python - <<'PY'
from importlib.metadata import version

for name in ("almasix", "almasix-orbit", "almasix-conduit"):
    print(f"  {name} {version(name)}")
PY
echo "OK — PyPI almasix / almasix-orbit / almasix-conduit installed."
echo "Next: source .venv/bin/activate && smith migrate --seed && smith serve"
echo "Demo login: demo@orbit.test / secret"
