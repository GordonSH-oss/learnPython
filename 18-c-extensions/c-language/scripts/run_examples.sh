#!/usr/bin/env bash
set -euo pipefail

for program in build/examples/*; do
    if [[ -f "$program" && -x "$program" ]]; then
        "$program" >/dev/null
    fi
done

echo "All examples ran successfully."
