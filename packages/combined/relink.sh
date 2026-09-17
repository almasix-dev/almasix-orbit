#!/usr/bin/env bash
# Recreate symlinks under packages/combined/src/almasix/orbit → split packages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/packages/combined/src/almasix/orbit"
mkdir -p "$DEST"

rel() { echo "../../../../$1/src/almasix/orbit/$2"; }

cd "$DEST"
rm -rf ./*
ln -s "$(rel panels __init__.py)" __init__.py
ln -s "$(rel panels provider.py)" provider.py
ln -s "$(rel panels testing.py)" testing.py
ln -s "$(rel panels py.typed)" py.typed
ln -s "$(rel panels panels)" panels
ln -s "$(rel panels resources)" resources
ln -s "$(rel support support)" support
ln -s "$(rel schemas schemas)" schemas
ln -s "$(rel forms forms)" forms
ln -s "$(rel tables tables)" tables
ln -s "$(rel actions actions)" actions
ln -s "$(rel infolists infolists)" infolists
ln -s "$(rel notifications notifications)" notifications
ln -s "$(rel widgets widgets)" widgets
ln -s "$(rel query-builder query_builder)" query_builder
echo "relinked $DEST"
