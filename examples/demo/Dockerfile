# Production image for the Orbit Records demo (Render / any Docker host).
#
# Build from the monorepo root (so packages/combined is available):
#   docker build -f examples/demo/Dockerfile -t orbit-demo .
#
# Almasix + Conduit come from PyPI; Orbit is installed from this checkout.

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

COPY examples/demo/ /app/
COPY packages/combined /tmp/orbit-combined

RUN pip install --no-cache-dir \
      "almasix[conduit]>=0.9.4" \
      "almasix-conduit>=0.2.1" \
      /tmp/orbit-combined \
      . \
    && rm -rf /tmp/orbit-combined \
    && mkdir -p /app/database /app/storage/app /app/public/vendor/orbit \
    && python - <<'PY'
from importlib import resources
from pathlib import Path

dest = Path("/app/public/vendor/orbit")
dest.mkdir(parents=True, exist_ok=True)
root = resources.files("almasix.orbit")
for rel, name in (
    ("resources/css/orbit.css", "orbit.css"),
    ("resources/js/orbit.js", "orbit.js"),
    ("resources/vendor/filepond.bundle.min.js", "filepond.bundle.min.js"),
    ("resources/vendor/filepond.bundle.min.css", "filepond.bundle.min.css"),
):
    src = root.joinpath(rel)
    if src.is_file():
        (dest / name).write_bytes(src.read_bytes())
        print("copied", rel)
    else:
        raise SystemExit(f"missing packaged asset: {rel}")
PY

EXPOSE 8000

COPY examples/demo/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
