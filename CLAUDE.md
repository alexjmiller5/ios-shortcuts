# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains iOS Shortcuts written in [Cherri](https://cherrilang.org/), a programming language that compiles to `.shortcut` files for the iOS Shortcuts app. The folder structure mirrors the Shortcuts app organization on iOS.

## Compiling Shortcuts

**Basic compilation:**
```bash
cherri <file.cherri>
```

**Compilation with secrets and constants:**
```bash
./scripts/compile-shortcut.sh <file1.cherri> [file2.cherri] ...
```

The compile script processes files in this order:
1. Substitutes `<<constant:NAME>>` with values from `constants.txt`
2. Converts `<<secret:NAME>>` to `op://Personal/NAME/credential`
3. Runs `op inject` to substitute actual secret values from 1Password
4. Compiles with `cherri`

## Secrets and Constants

### Secrets (`<<secret:NAME>>`)
Stored in 1Password under the "Personal" vault with the "Developer Credentials" tag. Referenced as:
```cherri
@ClientID = "<<secret:SPOTIFY_CLIENT_ID>>"
"Authorization": "Bearer <<secret:NOTION_INTEGRATION_SECRET>>"
```

### Constants (`<<constant:NAME>>`)
Stored in `constants.txt` at repo root in `KEY=value` format:
```
SYNAPSE_INTAKER_BASE_URL=https://example.com/api
```

Referenced as:
```cherri
jsonRequest("<<constant:SYNAPSE_INTAKER_BASE_URL>>?key=<<secret:API_KEY>>", "POST", { ... })
```

## Code Patterns

### Cherri Syntax Conventions

- **Metadata directives** at the top: `#define name`, `#define color`, `#define glyph`, `#define from sharesheet`
- **Includes** for action categories: `#include 'actions/web'`, `#include 'actions/scripting'`
- **Variables**: `@variableName = value` (mutable), `const name = value` (immutable)
- **String interpolation**: `"{variableName}"` within strings
- **Notion API calls**: Use `jsonRequest()` with headers including `Notion-Version: 2022-06-28`

### Type Handling
- Use `const Result = getName(variable)` then `@textVar = "{Result}"` to convert action outputs to text for conditionals
- `output()` expects text - place it inside if blocks when the else branch uses `nothing()`

## Directory Structure

- `notion/` - Shortcuts that interact with Notion databases and Synapse intaker
- `miscellaneous/` - Standalone utility shortcuts (Shazam→Spotify, etc.)
- `connectivity/` - Network-related shortcuts
- `notes-shortcuts/` - Apple Notes shortcuts
- `files-for-cherri-gem/` - Documentation files for a custom Cherri Gemini gem
- `scripts/` - Build scripts (`compile-shortcut.sh`)
- `constants.txt` - Non-sensitive constants for compilation

## Cherri Best Practices

- Use `const` instead of `@` variables when values won't change (reduces compiled action count)
- Use `nothing()` after actions with unused outputs to clear runtime memory
- Avoid large pre-defined arrays; prefer dictionaries for better performance
- Use raw text (single quotes) when string interpolation isn't needed

## Additional Resources

- Reference the Cherri lang documentation at `/Users/alexmiller/Desktop/software/reference-repos/cherrilang.org/language` for language features and standard library functions
