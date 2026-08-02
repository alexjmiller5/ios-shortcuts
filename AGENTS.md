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
- `miscellaneous/` - Standalone utility shortcuts (Shazam→Spotify, Spotify Reauth, etc.)
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
- **Read HTTP-response values with `getValue(getDictionary(@resp), "key")` — NOT `@resp['key']`.** `formRequest`/`downloadURL`/`jsonRequest` return a "Contents of URL" value, not a `dictionary`. The `['key']` syntax compiles to an inline *property aggrandizement*, not a real "Get Value" action — and it does NOT coerce the response, so at runtime it silently reads nothing (or returns the whole blob). The combination that works: `@respDict = getDictionary(@resp)` ("Get Dictionary from Input") then `@x = getValue(@respDict, "key")` ("Get Value from Dictionary"). Verify with `cherri <file> -d` and grep the `.plist` for `detect.dictionary` + `getvalueforkey`; `WFPropertyVariableAggrandizement` on a response means the lookup is broken. Nested keys must be walked one level at a time (`getValue` can't resolve a dotted path like `tracks.items`); same coercion applies to a list item before reading from it (`getDictionary(getFirstItem(...))`).

## User-token OAuth reauthorization pattern

For shortcuts that act on behalf of a user (e.g. Spotify), the user refresh token
is baked into the shortcut at compile time for speed. When it expires (Spotify:
every 6 months as of 2026-07-20), the shortcut detects `invalid_grant` (an empty
access token after a `refresh_token` request), discards it without retrying, and
queues any in-flight work so it isn't lost. A separate on-device reauth shortcut
(`spotify_reauth.cherri`) runs the Authorization Code flow without a Mac as a
**two-run, clipboard-driven flow** — run 1 opens the authorize page (`openURL` as
the last action) and ends; run 2 reads the redirect URL the user copied via
`getClipboard`, then `matchText("code=([^&]+)")` + `getMatchGroup(matches, 1)`
extracts the code → exchange for a new token → `setClipboard` so it can be pasted
into the main shortcut's `RefreshToken` field. Two runs because iOS foregrounds
an in-shortcut `prompt` the instant `openURL` opens Safari, so a single-run prompt
pops over the user before they've approved; the clipboard handoff avoids any
blocking modal during the Safari step. No PKCE needed since the client secret is
embedded. See `docs/superpowers/specs/2026-06-26-spotify-reauth-design.md`.

## Additional Resources

- Reference the Cherri lang documentation at https://cherrilang.org for language features and standard library functions

## My Specifications to you

- Whenever you make any changes to a shortcut, run it through the cherri compiler to ensure validity - at least it's able to compile