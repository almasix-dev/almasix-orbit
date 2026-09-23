#!/usr/bin/env sh
# Boot: ensure SQLite schema + demo seed, optional scheduler, then serve.
set -eu
PORT="${PORT:-8000}"
mkdir -p "$(dirname "${DB_DATABASE:-/app/database/database.sqlite}")"
smith migrate --force --seed

# Soft catalog resets (demo:reset) on the schedule in routes/console.py.
# Cookie sessions stay valid because users are never wiped.
if [ "${DEMO_SCHEDULE:-1}" = "1" ]; then
  smith schedule:work &
fi

exec smith serve --host 0.0.0.0 --port "$PORT" --workers 1 --no-reload --proxy-headers
