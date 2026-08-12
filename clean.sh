#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

find "$ROOT" \
    \( \
        -name "__pycache__"  \
        -o -name "*.egg-info" \
        -o -name "*.pyc"     \
        -o -name "dist"      \
        -o -name "build"     \
        -o -name ".venv"     \
        -o -name ".history"  \
    \) \
    -prune -print -exec rm -rf {} \;

echo "Clean."
