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
@ApiKey = "<<secret:SERVICE_API_KEY>>"
"Authorization": "Bearer <<secret:NOTION_INTEGRATION_SECRET>>"
```

The compile script expands these to fields of a single `iOS Shortcuts ENV`
item (`op://<vault-id>/<item-id>/NAME`). Adapt the `VAULT` / `ENV_ITEM` IDs in
`scripts/compile-shortcut.sh` to your own 1Password setup. `op inject` streams
values through a private named pipe into Cherri; it never writes injected
plaintext `.cherri` source to a regular file.

Cherri v2.3 accepts this FIFO input, but native `shortcuts sign` rejects FIFO
and `/dev/fd` input on the tested macOS. The compiler's unsigned binary therefore
exists briefly as a mode-600 file in a mode-700 build directory. After the plist
patch, signing writes to a staged file. Only successful signing replaces the
usual `<source-directory>/<shortcut-name>.shortcut` destination, which contains
the runtime credential by design. Build errors and INT/TERM/HUP stop active
children and remove unsigned/partial signed outputs. SIGKILL, an OS crash, or
power loss cannot run cleanup and can leave the private `.compile-shortcut.*`
directory beside the source.

Tool diagnostics are suppressed to avoid quoting injected credentials. Diagnose
compiler errors with a dummy scratch source and `cherri --skip-sign`. The focused
build regression requires macOS, Python 3 and Cherri, uses dummy credentials and
stub injection/signing, and never contacts a vault or installs/runs a shortcut:

```bash
python3 scripts/test-compile-shortcut.py
```

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

## Cochlea capture and Shortcut cutover

Cochlea owns recording, offline signatures, recognition, background delivery and
capture notifications. In Shortcuts, choose **Cochlea → Capture song**, the
built-in App Shortcut. On iOS 18+, **Cochlea → Capture song** is also available
as a native Lock Screen or Control Center control with a waveform icon. This
path uses the app's Keychain enrollment and needs no credentials in a Shortcut.

### Phone acceptance

1. Install the approved signed Cochlea build and confirm its version. Open the
   existing device enrollment link if it is not connected. Allow microphone,
   notifications and Live Activities when prompted.
2. Run **Cochlea → Capture song** with music playing. Verify the song and artist
   in the Live Activity, one song-recognized notification, and the song in the
   destination Spotify playlist. A successful upload or Spotify addition must
   not create another success alert.
3. Repeat the same song. Verify there is no duplicate playlist entry. With the
   service operator, verify the corresponding capture receipt and provenance.
4. Run from the chosen Lock Screen control and after swiping the app away.
   Verify capture, cancellation and visible song/no-match/saved-for-later
   results. Verify an offline capture survives and resolves on the next online
   use. Report any system permission prompt that prevents the flow.
5. Verify a definite Spotify-add failure produces an actionable error without
   losing the capture. A timeout or generic server error does not prove Spotify
   failed to add it; the service must distinguish an unconfirmed result from a
   confirmed failure.
