# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains iOS Shortcuts written in [Cherri](https://cherrilang.org/), a programming language that compiles to `.shortcut` files for the iOS Shortcuts app. The folder structure mirrors the Shortcuts app organization on iOS.

## Compiling Shortcuts

**Basic compilation:**
```bash
cherri <file.cherri>
```

**Compilation with secrets (using 1Password CLI):**
```bash
./scripts/compile-with-op.sh <file1.cherri> <file2.cherri> ...
```

The `compile-with-op.sh` script uses `op inject` to substitute secret placeholders (like `NOTION_INTEGRATION_SECRET`, `NOTION_VIDEO_DATABASE_ID`) with values from 1Password before compilation.

## Code Patterns

### Cherri Syntax Conventions

Shortcuts use these common patterns:

- **Metadata directives** at the top: `#define name`, `#define color`, `#define glyph`
- **Includes** for action categories: `#include 'actions/web'`
- **Variables**: `@variableName = value` (mutable), `const name = value` (immutable)
- **String interpolation**: `"{variableName}"` within strings
- **Notion API calls**: Use `jsonRequest()` with proper headers including `Notion-Version: 2022-06-28`

### Secret Handling

Secrets are referenced as plain identifiers (e.g., `NOTION_INTEGRATION_SECRET`) in `.cherri` files. The `op inject` tool replaces these with actual values during compilation. Never commit compiled `.shortcut` files or `.env.local`.

## Directory Structure

- `notion/` - Shortcuts that interact with Notion databases
- `miscellaneous/` - Standalone utility shortcuts
- `connectivity/` - Network-related shortcuts
- `notes-shortcuts/` - Apple Notes shortcuts
- `files-for-cherri-gem/` - Documentation files for a custom Cherri Gemini gem

## Cherri Best Practices

- Use `const` instead of `@` variables when values won't change (reduces compiled action count)
- Use `nothing()` after actions with unused outputs to clear runtime memory
- Avoid large pre-defined arrays; prefer dictionaries for better performance
- Use raw text (single quotes) when string interpolation isn't needed

## Additional Resources

- Please reference the Cherri lang documentation when writing cherri code which is located at `/Users/alexmiller/Desktop/software/reference-repos/cherrilang.org/language`. This has all the specific docs on the language features and standard library functions and is especially important because this is a small, new language with a small community.