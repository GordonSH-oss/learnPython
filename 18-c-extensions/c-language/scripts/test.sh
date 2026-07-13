#!/usr/bin/env bash
set -euo pipefail

assert_output() {
    local expected="$1"
    shift
    local actual
    actual=$("$@")
    if [[ "$actual" != "$expected" ]]; then
        printf 'Expected:\n%s\nActual:\n%s\n' "$expected" "$actual" >&2
        exit 1
    fi
}

assert_output "32.0" bash -c "printf '0\n' | build/solutions/01_temperature"
assert_output "min=-2 max=11 mean=5.20" build/solutions/03_statistics
assert_output "0 1 4 9 16 25 36 49 64 81" build/solutions/06_dynamic_vector

sample=$(mktemp)
trap 'rm -f "$sample"' EXIT
printf 'hello C\nsecond line\n' >"$sample"
assert_output "lines=2 words=4 chars=20" build/solutions/07_word_count "$sample"

bash scripts/run_examples.sh
echo "All solution checks passed."
