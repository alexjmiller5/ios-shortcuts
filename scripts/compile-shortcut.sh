#!/usr/bin/env bash
set -euo pipefail
umask 077

VAULT="uk3hfwomwjxl33uxpjurzpr7z4"  # "iOS Shortcuts" vault (id - rename-proof)
ENV_ITEM="p6cdlljtfcdwbyzznatrcmohdi"  # ENV item id, one field per <<secret:NAME>>
CONSTANTS_FILE="constants.txt"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file1.cherri> [file2.cherri] ..."
    exit 1
fi

# Function to substitute constants. constants.local.txt (untracked) is applied
# first so machine-specific values win over the committed placeholders.
substitute_constants() {
    local input_file="$1"
    local output_file="$2"

    cp "$input_file" "$output_file"

    for constants_file in "constants.local.txt" "$CONSTANTS_FILE"; do
        [ -f "$constants_file" ] || continue
        while IFS='=' read -r key value || [ -n "$key" ]; do
            # Skip empty lines and comments
            [[ -z "$key" || "$key" =~ ^# ]] && continue
            # Substitute <<constant:KEY>> with value
            sed -i '' "s|<<constant:${key}>>|${value}|g" "$output_file"
        done < "$constants_file"
    done
}

for file in "$@"; do
    if [ ! -f "$file" ]; then
        echo "Warning: File '$file' not found. Skipping."
        continue
    fi

    temp_dir=""
    inject_pid=""
    build_pid=""
    cleanup() {
        # Stop writers before unlinking their outputs, including a producer
        # blocked opening the FIFO if Cherri fails before reading it.
        for pid in "$inject_pid" "$build_pid"; do
            [ -n "$pid" ] || continue
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        done
        if [ -n "$temp_dir" ]; then
            shopt -s dotglob  # Shortcut names can start with a dot.
            rm -f "$temp_dir"/*
            rmdir "$temp_dir"
        fi
    }
    trap cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    trap 'exit 129' HUP

    dir_name=$(cd "$(dirname "$file")" && pwd)
    temp_dir=$(mktemp -d "${dir_name}/.compile-shortcut.XXXXXX")
    temp_file="$temp_dir/input.cherri"
    echo "Processing $file..."

    substitute_constants "$file" "$temp_dir/constants.cherri"
    sed -E "s|<<secret:([A-Za-z_][A-Za-z0-9_]*)>>|op://${VAULT}/${ENV_ITEM}/\1|g" \
        "$temp_dir/constants.cherri" > "$temp_dir/references.txt"
    mkfifo "$temp_file"

    # Cherri v2.3 reads FIFO input. Plaintext source exists only in the pipe.
    # Suppress tool diagnostics: compiler errors can quote injected source.
    op inject -i "$temp_dir/references.txt" > "$temp_file" 2>/dev/null &
    inject_pid=$!
    (cd "$dir_name" && exec cherri "$temp_file" --skip-sign) >/dev/null 2>&1 &
    build_pid=$!
    if ! wait "$build_pid"; then
        echo "Error: compilation failed; validate with dummy credentials for diagnostics." >&2
        exit 1
    fi
    build_pid=""
    if ! wait "$inject_pid"; then
        echo "Error: secret injection failed." >&2
        exit 1
    fi
    inject_pid=""

    shortcut_name=$(sed -n 's/^#define name //p' "$file" | head -1)
    unsigned="$temp_dir/${shortcut_name}_unsigned.shortcut"
    python3 "$(dirname "$0")/patch-shortcut-plist.py" "$unsigned" >/dev/null 2>&1 &
    build_pid=$!
    if ! wait "$build_pid"; then
        echo "Error: plist patch failed." >&2
        exit 1
    fi
    build_pid=""

    # macOS signing requires a regular input file. Keep it private, clean
    # both outputs on failure, and replace the destination only on success.
    shortcuts sign -i "$unsigned" -o "$temp_dir/signed.shortcut" >/dev/null 2>&1 &
    build_pid=$!
    if ! wait "$build_pid"; then
        echo "Error: signing failed." >&2
        exit 1
    fi
    build_pid=""
    mv -f "$temp_dir/signed.shortcut" "$dir_name/${shortcut_name}.shortcut"
    cleanup
    trap - EXIT INT TERM HUP
done
echo "Done."
