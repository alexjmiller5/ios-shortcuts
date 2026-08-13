#!/usr/bin/env bash
set -e

VAULT="Personal"
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

    # Create hidden temp files in the same directory as the source
    # This ensures the compiled output lands in the correct folder
    dir_name=$(dirname "$file")
    base_name=$(basename "$file")
    temp_file="${dir_name}/.tmp_${base_name}"
    temp_file_constants="${dir_name}/.tmp1_${base_name}"
    temp_file_secrets="${dir_name}/.tmp2_${base_name}"

    # cleanup trap to ensure temp files are deleted even on error
    trap 'rm -f "$temp_file" "$temp_file_constants" "$temp_file_secrets"' EXIT

    echo "🔐 Processing $file..."

    # Step 1: Substitute <<constant:NAME>> with values from constants.txt
    substitute_constants "$file" "$temp_file_constants"

    # Step 2: Convert <<secret:NAME>> to op://VAULT/NAME/credential
    sed -E "s|<<secret:([A-Za-z_][A-Za-z0-9_]*)>>|op://${VAULT}/\1/credential|g" "$temp_file_constants" > "$temp_file_secrets"

    # Step 3: Run op inject to substitute the op:// references
    op inject -i "$temp_file_secrets" -o "$temp_file"

    echo "🍒 Compiling $base_name..."
    # cherri resolves embedFile() paths relative to its CWD, not the source
    # file — compile from the file's directory so "assets/..." references work
    (cd "$dir_name" && cherri ".tmp_${base_name}")

    # Clean up immediately for this iteration
    rm -f "$temp_file" "$temp_file_constants" "$temp_file_secrets"
    trap - EXIT
done
echo "✨ Done."
