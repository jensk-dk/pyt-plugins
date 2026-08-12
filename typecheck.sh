#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

MYPYPATH="myapp-plugin-sdk:myapp-example-plugins1:myapp-example-plugins2:myapp" \
    python3 -m mypy \
        myapp-plugin-sdk/myapp_plugin_sdk \
        myapp-example-plugins1/myapp_example_plugin1 \
        myapp-example-plugins2/myapp_example_plugin2 \
        myapp \
        --config-file pyproject.toml
