# iOS Shortcuts

## About This Repo

- The folder structure of the shortcuts will mirror the structure of the folder in my iCloud Shortcuts apps
- The shortcuts will be written in [Cherri](https://cherrilang.org/)

## Prerequisites

- [Cherri](https://cherrilang.org/) — the `cherri` compiler
- [1Password CLI](https://developer.1password.com/docs/cli/) (`op`) — only needed to compile shortcuts that use `<<secret:NAME>>`

## Compiling Shortcuts

The shortcuts can be compiled to a `.shortcut` file which can be imported into the Shortcuts app on iOS.

**Basic compilation (no secrets):**
```bash
cherri <file.cherri>
```

**Compilation with secrets and constants:**
```bash
./scripts/compile-shortcut.sh <file1.cherri> [file2.cherri] ...
```

**Using just (recommended):**
```bash
just compile <file.cherri>           # Compile specific file(s)
just compile-dir <directory>         # Compile all .cherri files in a directory
just compile-all                     # Compile all shortcuts in the repo
```

### Secrets

Secrets are stored in 1Password and referenced in `.cherri` files using the `<<secret:NAME>>` syntax:

```cherri
@ClientID = "<<secret:SPOTIFY_CLIENT_ID>>"
"Authorization": "Bearer <<secret:NOTION_INTEGRATION_SECRET>>"
```

The compile script expands these to fields of a single `iOS Shortcuts ENV` item (`op://<vault>/iOS Shortcuts ENV/NAME`) and uses the 1Password CLI (`op inject`) to substitute actual values at compile time — adapt the `VAULT` / `ENV_ITEM` variables in `scripts/compile-shortcut.sh` to your own 1Password setup.

### Constants

Non-sensitive constants are stored in `constants.txt` at the repo root in `KEY=value` format:

```
# constants.txt
SYNAPSE_INTAKER_BASE_URL=https://example.com/api
```

Reference them in `.cherri` files using `<<constant:NAME>>`:

```cherri
jsonRequest("<<constant:SYNAPSE_INTAKER_BASE_URL>>?key=<<secret:API_KEY>>", "POST", { ... })
```

Environment-specific values in `constants.txt` are
committed as placeholders. Set your real values in an untracked
`constants.local.txt` (same `KEY=value` format) — the compile script applies it
first, so it overrides `constants.txt`.

## Permission prompts on reinstall

Shortcuts privacy grants ("Always Allow" for each domain/app) are keyed to the
shortcut *instance*, so reimporting a recompiled `.shortcut` always re-prompts —
there is no workaround. Mitigations: Settings → Shortcuts → Advanced toggles
(Allow Running Scripts, Allow Sharing Large Amounts of Data) reduce some prompt
classes, and in-editor edits (as opposed to reimports) keep existing grants.
The wrapper architecture helps too: pinned wrappers are rarely reinstalled and
keep their grants.

## Shazam → Spotify capture client

`shortcuts/shazam_right_pointing_arrow_spotify.cherri` recognizes a song and
POSTs `title`, `artist`, `apple_music_id`, and `shazam_url` as JSON to
`MUSIC_SYNC_CAPTURE_URL`. It sends `Modal-Key` and `Modal-Secret` headers from
`MODAL_KEY` and `MODAL_SECRET` in the `iOS Shortcuts ENV` item. The caller needs
only the capture endpoint and these auth headers. Matching, playlist selection,
and storage are owned by the service.

The response is explicitly converted to a dictionary before reading `message`,
which is shown as a notification. Unrecognized audio stops before the request;
an empty message produces a failure notification. Shortcuts may stop on a
transport/HTTP error or an invalid dictionary response before that notification.
Compilation does not verify these runtime behaviors.

### Build and pending cutover

The source is prepared for `/capture`; it has **not been installed or verified
on the phone**. Retained `.shortcut` binaries are fallback artifacts, not builds
of this capture-client source. Keep the installed shortcuts, `spotify_reauth.cherri`,
Reauth design document, all existing binaries, `SPOTIFY_REDIRECT_URI`, Spotify
credential fields, and the Spotify developer app until phone E2E passes.

For source validation without credentials, substitute placeholders with dummy
values in a scratch copy and run `cherri <scratch-file.cherri> --skip-sign -d`.
Inspect the plist for the endpoint, POST JSON body, auth headers, and
`detect.dictionary` followed by `getvalueforkey` for `message`. Do not import
that dummy build. The regular compile script injects real secrets and signs
output, so it is not the dummy-validation path.

Pending integration, in order:

1. Confirm the capture service is ready. Set its endpoint in untracked
   `constants.local.txt` as `MUSIC_SYNC_CAPTURE_URL=<capture-endpoint>` and
   ensure the caller's `MODAL_KEY` / `MODAL_SECRET` fields are provisioned.
2. Preserve the fallback artifacts, then build the source with
   `just compile shortcuts/shazam_right_pointing_arrow_spotify.cherri`.
   This uses local constant overrides, injects the ENV item fields, compiles
   unsigned, applies plist patches, and signs the `.shortcut`. It replaces
   the output binary at `shortcuts/Shazam → Spotify.shortcut` if present.
3. Import the signed build on the Mac and transfer/import it on the phone,
   replacing the installed Shazam shortcut. Reimports prompt for permissions.
4. On the phone, recognize a song: verify the service's added notification,
   the song in `new songs`, and the corresponding Shazam provenance record
   through the service's catalog verification. Repeat the same song and verify
   the already-present notification without duplication. Report both results.
5. Only after successful phone E2E, perform the separately approved cutover:
   retire Spotify Reauth on both devices, its source and design document,
   fallback binaries, old Spotify credential fields and redirect constant,
   and the old shortcut's Spotify developer app. Update documentation then.
