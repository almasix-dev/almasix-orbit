#!/usr/bin/env bash
# Install Orbit Demo. Prefers local Almasix / Orbit / Conduit checkouts (same
# layout as orbit-admin) so the demo can exercise the latest panel APIs.
# Falls back to production PyPI when siblings are missing (Docker / Render).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"          # examples/demo
REPO="$(cd "$ROOT/../.." && pwd)"             # almasix-orbit
ALMASIX="$(cd "$REPO/../almasix" && pwd)"
CONDUIT="$(cd "$REPO/../almasix-conduit" && pwd)"

cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel

if [[ -f "$ALMASIX/pyproject.toml" && -f "$CONDUIT/pyproject.toml" && -f "$REPO/packages/combined/pyproject.toml" ]]; then
  ln -sfn "$REPO/packages/combined/src/almasix/orbit" "$ALMASIX/src/almasix/orbit"
  pip install -e "${ALMASIX}[conduit]"
  pip install -e "$CONDUIT"
  pip install -e "$REPO/packages/combined"
  pip install -e .
  echo "OK — local Almasix / Orbit / Conduit editables installed."
else
  pip install -e .
  echo "OK — PyPI almasix / almasix-orbit / almasix-conduit installed."
fi

python - <<'PY'
from importlib.metadata import version

for name in ("almasix", "almasix-orbit", "almasix-conduit"):
    print(f"  {name} {version(name)}")
PY
echo "Next: source .venv/bin/activate && smith migrate --seed && smith serve"
echo "Demo login: demo@orbit.test / secret"
