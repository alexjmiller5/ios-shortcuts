default:
    @just --list

# Compile cherri files with secrets and constants
build +files:
    ./scripts/compile-with-op.sh {{files}}

# Compile all cherri files in a directory
build-dir dir:
    ./scripts/compile-with-op.sh {{dir}}/*.cherri

# Compile all shortcuts
build-all:
    ./scripts/compile-with-op.sh notion/*.cherri miscellaneous/*.cherri
