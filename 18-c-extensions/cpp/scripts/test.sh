#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_examples.sh

for program in build/solutions/*; do
    if [[ -f "$program" && -x "$program" ]]; then
        "$program" >/dev/null
    fi
done

echo "All C++ checks passed."

