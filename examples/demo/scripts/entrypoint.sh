#!/usr/bin/env sh
# Boot: ensure SQLite schema + demo seed, then serve.
set -eu
PORT="${PORT:-8000}"
mkdir -p "$(dirname "${DB_DATABASE:-/app/database/database.sqlite}")"
smith migrate --force --seed
exec smith serve --host 0.0.0.0 --port "$PORT" --workers 1 --no-reload --proxy-headers
