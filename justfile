default:
    @just --list

# Compile cherri files with secrets and constants
compile +files:
    ./scripts/compile-shortcut.sh {{files}}

# Compile all cherri files in a directory
compile-dir dir:
    ./scripts/compile-shortcut.sh {{dir}}/*.cherri

# Compile all shortcuts
compile-all:
    ./scripts/compile-shortcut.sh notion/*.cherri miscellaneous/*.cherri
