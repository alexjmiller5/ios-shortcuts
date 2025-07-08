#!/bin/bash

# Temporarily inject secrets from a .env file into source files,
# run a command, and then clean up.

set -e

# --- Configuration ---
ENV_FILE=".env.local"
COMMAND_TO_RUN="cherri"

# --- Pre-flight Checks ---

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file '$ENV_FILE' not found." >&2
    exit 1
fi

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <file1> [<file2> ...]" >&2
    echo "Injects secrets from $ENV_FILE into files, runs '$COMMAND_TO_RUN', and cleans up." >&2
    exit 1
fi

if ! command -v $COMMAND_TO_RUN &>/dev/null; then
    echo "Error: Command '$COMMAND_TO_RUN' not found. Please ensure it's installed and in your PATH." >&2
    exit 1
fi

# --- Main Logic ---

sed_expressions=()
while IFS='=' read -r key value || [[ -n "$key" ]]; do
    # Skip comments and empty lines.
    if [[ "$key" =~ ^\s*# ]] || [[ -z "$key" ]]; then
        continue
    fi

    # Sanitize key and value by removing potential carriage returns from DOS-style line endings.
    key=${key%$'\r'}
    value=${value%$'\r'}

    # Escape characters for the sed replacement string.
    escaped_value=$(printf '%s\n' "$value" | sed -e 's/[\\/&]/\\&/g')

    # Add the substitution command to our array.
    # Use [[:<:]] and [[:>:]] for word boundaries for better portability (works on GNU and BSD/macOS sed).
    sed_expressions+=(-e "s/[[:<:]]${key}[[:>:]]/${escaped_value}/g")

done <"$ENV_FILE"
if [ "${#sed_expressions[@]}" -eq 0 ]; then
    echo "Warning: No secrets found or parsed from '$ENV_FILE'."
fi

for file in "$@"; do
    if [ ! -f "$file" ]; then
        echo "Warning: File '$file' not found. Skipping."
        continue
    fi

    # Create a secure temporary file with a .cherri extension.
    # This is often required by compilers that check the file extension.
    temp_file=$(mktemp "${TMPDIR:-/tmp}/cherri-temp.XXXXXX.cherri")
    trap 'rm -f "$temp_file"' EXIT INT TERM

    echo "Processing '$file'..."

    # Perform all substitutions and write to the temp file.
    sed "${sed_expressions[@]}" "$file" >"$temp_file"

    echo "Running command: $COMMAND_TO_RUN \"$temp_file\""

    # Execute the command with the temporary file.
    # $COMMAND_TO_RUN "$temp_file"

    echo "Successfully processed '$file'."

    # --- PAUSE FOR DEBUGGING ---
    # The script will now pause so you can inspect the temporary file.
    echo "---"
    echo "DEBUG: Paused before cleanup."
    echo "You can inspect the temp file at: $temp_file"
    echo "Press [Enter] to continue and delete the file."
    read -r
    # --- END DEBUGGING ---

    # Clean up the temp file for this iteration.
    echo "Resuming script and deleting temp file..."
    rm -f "$temp_file"
    trap - EXIT INT TERM
done

echo "All files processed successfully."
