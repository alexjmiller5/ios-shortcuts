# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

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

The compile script processes each file in a private build directory:

1. Substitutes `<<constant:NAME>>` from untracked `constants.local.txt` first, then `constants.txt` for defaults
2. Converts `<<secret:NAME>>` to `op://<VAULT>/<ENV_ITEM>/NAME`; both references in the script are stable IDs
3. Streams `op inject` output through a mode-600 named pipe into Cherri, never a regular plaintext source file
4. Compiles with `cherri --skip-sign` from the source directory for `embedFile()` paths; unsigned output stays in the mode-700 build directory
5. Applies `scripts/patch-shortcut-plist.py`, then signs to a staged file and replaces the signed destination only after success

Cherri v2.3 supports FIFO source input. Native `shortcuts sign` requires a
regular input file on the tested macOS; FIFO and `/dev/fd` inputs fail with
"The file couldn’t be opened because it isn’t in the correct format."
The unsigned credential-bearing binary is therefore transiently on disk with
mode 600. EXIT/INT/TERM/HUP cleanup stops active children and removes the build
directory, including unsigned and partial signed outputs. SIGKILL, OS crashes,
and power loss cannot run shell traps and can leave that private directory.

Injected tool output is suppressed because diagnostics can quote credentials.
For compiler diagnostics use only placeholder/dummy scratch sources. Run the
focused regression with `python3 scripts/test-compile-shortcut.py`: it uses real
Cherri, stub injection/signing, dummy constants and assets, and no vault calls.

## Secrets and Constants

### Secrets (`<<secret:NAME>>`)
Stored as fields of the single `iOS Shortcuts ENV` item in the vault selected
by `scripts/compile-shortcut.sh`. Referenced as:
```cherri
@ClientID = "<<secret:SPOTIFY_CLIENT_ID>>"
"Authorization": "Bearer <<secret:NOTION_INTEGRATION_SECRET>>"
```

### Constants (`<<constant:NAME>>`)
Stored in `constants.txt` at repo root in `KEY=value` format. Environment-specific
values are placeholders; untracked `constants.local.txt` overrides them:
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
- `shortcuts/` - Standalone utility shortcuts (Shazam→Spotify, Spotify Reauth, etc.) - mirrors the phone's "Shortcuts" folder
- `shortcuts/assets/` - Binary assets embedded at compile time via `embedFile()` (Water Eject tone, Mario waow)
- `scripts/` - Build scripts (`compile-shortcut.sh`)
- `constants.txt` - Non-sensitive constants for compilation

## Cherri Best Practices

- Use `const` instead of `@` variables when values won't change (reduces compiled action count)
- Use `nothing()` after actions with unused outputs to clear runtime memory
- Avoid large pre-defined arrays; prefer dictionaries for better performance
- Use raw text (single quotes) when string interpolation isn't needed
- **Read HTTP-response values with `getValue(getDictionary(@resp), "key")` - NOT `@resp['key']`.** `formRequest`/`downloadURL`/`jsonRequest` return a "Contents of URL" value, not a `dictionary`. The `['key']` syntax compiles to an inline *property aggrandizement*, not a real "Get Value" action - and it does NOT coerce the response, so at runtime it silently reads nothing (or returns the whole blob). The combination that works: `@respDict = getDictionary(@resp)` ("Get Dictionary from Input") then `@x = getValue(@respDict, "key")` ("Get Value from Dictionary"). Verify with `cherri <file> -d` and grep the `.plist` for `detect.dictionary` + `getvalueforkey`; `WFPropertyVariableAggrandizement` on a response means the lookup is broken. Nested keys must be walked one level at a time (`getValue` can't resolve a dotted path like `tracks.items`); same coercion applies to a list item before reading from it (`getDictionary(getFirstItem(...))`).

## Shazam capture source and validation

`shortcuts/shazam_right_pointing_arrow_spotify.cherri` is a capture-service
client: Shazam metadata -> one JSON POST -> dictionary coercion -> `message`
notification. Its only configuration is `MUSIC_SYNC_CAPTURE_URL`, `MODAL_KEY`,
and `MODAL_SECRET`; provider credentials, playlist IDs, and storage details
belong to the service.

Validate without secrets by substituting dummy values in a scratch copy, then
running `cherri <scratch-file.cherri> --skip-sign -d`. Inspect the plist's URL,
POST method, four JSON fields, auth headers, and explicit response dictionary
conversion before the `message` lookup. Do not use the regular compile script
for dummy validation: it injects real credentials and signs the output.

Source and installed/binary versions must not be assumed identical. Retain
fallback sources, binaries, Reauth documentation, redirect constant, credentials,
and the developer app until phone E2E confirms both added and already-present
results. The README holds the pending cutover sequence. Compiling is not phone
E2E and does not authorize installation or fallback deletion.

## Additional Resources

- Reference the Cherri lang documentation at https://cherrilang.org for language features and standard library functions

## My Specifications to you

- Whenever you make any changes to a shortcut, run it through the cherri compiler to ensure validity - at least it's able to compile
