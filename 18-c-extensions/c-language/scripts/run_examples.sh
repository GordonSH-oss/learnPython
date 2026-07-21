#!/usr/bin/env bash
set -euo pipefail

for program in build/examples/*; do
    name=$(basename "$program")
    if [[ "$name" == lib*.dylib || "$name" == lib*.so ]]; then
        continue
    fi
    if [[ "$name" == 19_socket && "${RUN_NETWORK_EXAMPLES:-0}" != 1 ]]; then
        continue
    fi
    if [[ -f "$program" && -x "$program" ]]; then
        "$program" >/dev/null
    fi
done

echo "All examples ran successfully."
