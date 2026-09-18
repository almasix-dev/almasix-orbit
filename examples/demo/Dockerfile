# Production image for the Orbit music catalog demo (Render / any Docker host).
# Build context: examples/demo (this directory).
# Dependencies come from PyPI via pyproject.toml (no path pins).

FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    APP_DEBUG=false \
    DB_CONNECTION=sqlite \
    DB_DATABASE=/app/database/database.sqlite \
    SESSION_DRIVER=cookie \
    SESSION_SECURE_COOKIE=true

COPY pyproject.toml README.md ./
COPY . .

RUN pip install --no-cache-dir . \
    && mkdir -p /app/database /app/public/vendor/orbit \
    && python - <<'PY'
from importlib import resources
from pathlib import Path

dest = Path("/app/public/vendor/orbit")
dest.mkdir(parents=True, exist_ok=True)
root = resources.files("almasix.orbit")
for rel, name in (("resources/css/orbit.css", "orbit.css"), ("resources/js/orbit.js", "orbit.js")):
    src = root.joinpath(rel)
    if src.is_file():
        (dest / name).write_bytes(src.read_bytes())
        print("copied", rel)
    else:
        raise SystemExit(f"missing packaged asset: {rel}")
PY

EXPOSE 8000

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
