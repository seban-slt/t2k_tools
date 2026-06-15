#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)
FIXTURES_DIR="$SCRIPT_DIR/fixtures"
OUTPUT_DIR="$SCRIPT_DIR/output"

TOOL="$REPO_DIR/t2k_new_format.py"
LOADER="${LOADER:-$FIXTURES_DIR/t2kf_new_format_ldr.xex}"
PYTHON="${PYTHON:-python3}"
CHKXEX="${CHKXEX:-chkxex}"

mkdir -p "$OUTPUT_DIR"

if [[ ! -f "$LOADER" ]]; then
    echo "error: missing loader: $LOADER" >&2
    exit 1
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "error: missing Python interpreter: $PYTHON" >&2
    exit 1
fi

if ! command -v "$CHKXEX" >/dev/null 2>&1; then
    echo "error: missing chkxex tool: $CHKXEX" >&2
    exit 1
fi

shopt -s nullglob
inputs=("$FIXTURES_DIR"/*.xex)

if ((${#inputs[@]} == 0)); then
    echo "error: no .xex files found in $FIXTURES_DIR" >&2
    exit 1
fi

tested=0

for input in "${inputs[@]}"; do
    if [[ "$input" == "$LOADER" ]]; then
        continue
    fi

    base=$(basename "$input" .xex)
    tape_name=$(printf '%s' "$base" | tr '[:lower:]' '[:upper:]' | tr -cd 'A-Z0-9_-' | cut -c 1-10)
    if [[ -z "$tape_name" ]]; then
        tape_name="NONAME"
    fi

    hex_out="$OUTPUT_DIR/$base.hex"
    cas_out="$OUTPUT_DIR/$base.cas"
    decoded_out="$OUTPUT_DIR/${base}_decoded.xex"
    loader_out="$OUTPUT_DIR/${base}_loader.xex"

    echo "==> $base"
    echo "    checking source XEX"
    "$CHKXEX" "$input" >/dev/null

    echo "    encoding HEX with loader"
    "$PYTHON" "$TOOL" \
        --encode \
        --add-loader "$LOADER" \
        --tape-name "$tape_name" \
        "$input" \
        "$hex_out" >/dev/null

    echo "    encoding CAS with loader"
    "$PYTHON" "$TOOL" \
        --encode \
        --format cas \
        --add-loader "$LOADER" \
        --tape-name "$tape_name" \
        "$input" \
        "$cas_out" >/dev/null

    echo "    decoding generated HEX"
    "$PYTHON" "$TOOL" \
        --skip-loader \
        --extract-loader "$loader_out" \
        "$hex_out" \
        "$decoded_out" >/dev/null

    echo "    checking decoded XEX"
    "$CHKXEX" "$decoded_out" >/dev/null

    echo "    comparing extracted loader"
    cmp -s "$LOADER" "$loader_out"

    tested=$((tested + 1))
done

if ((tested == 0)); then
    echo "error: no program .xex files tested; only loader was found" >&2
    exit 1
fi

echo "OK: tested $tested file(s)"
