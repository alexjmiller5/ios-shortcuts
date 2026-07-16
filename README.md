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

The compile script expands these to `op://Personal/NAME/credential` and uses the 1Password CLI (`op inject`) to substitute actual values. The `op://Personal/NAME/credential` references documented in this repo assume the author's vault layout — adapt the vault (the `VAULT` variable in `scripts/compile-shortcut.sh`) and item names to your own 1Password setup.

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

## Spotify token reauthorization

As of **2026-07-20**, Spotify refresh tokens expire every 6 months. The
`Shazam → Spotify` shortcut keeps its refresh token baked in (for speed), and a
companion `Spotify Reauth` shortcut mints a new one entirely on iPhone.

### One-time setup

1. In the [Spotify developer dashboard](https://developer.spotify.com/dashboard),
   add the redirect URI from `constants.txt` (`SPOTIFY_REDIRECT_URI`, default
   `http://127.0.0.1:8080/callback`) to the app's settings. It must match exactly.
   Spotify allows the `http://127.0.0.1` loopback address but **not** `localhost`,
   and requires HTTPS for any non-loopback URI.
2. Ensure these 1Password secrets (Personal vault) exist: `SPOTIFY_CLIENT_ID`,
   `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_SHAZAM_PLAYLIST_ID`, `SPOTIFY_REFRESH_TOKEN`.

### When the token expires

`Shazam → Spotify` detects the expired token (`invalid_grant`), queues the song
to Receptor so it isn't lost, and tells you to reauthorize. `Spotify Reauth` is a
**two-tap flow** (driven by the clipboard so nothing blocks the screen while
you're in Safari):

1. Run **Spotify Reauth**. It shows a brief note, then opens Spotify in Safari.
2. Approve access. You'll land on `http://127.0.0.1:8080/callback?code=...` —
   Safari can't load it (nothing's listening), but the URL is still in the address
   bar. **Copy that URL** and switch back to Shortcuts.
3. Run **Spotify Reauth again.** It reads the URL off your clipboard, exchanges it,
   and copies the new refresh token to your clipboard.
4. Open `Shazam → Spotify` in the Shortcuts editor and paste it into the
   `RefreshToken` text field.

> The shortcut tells run 1 from run 2 by checking whether the clipboard already
> contains a `code=...`. If you ever get stuck, copy anything without `code=`
> (or nothing) and it restarts from run 1.

### Caveats

- **Manual paste.** A running shortcut can't rewrite its own baked-in value, so
  the new token is pasted by hand. This is the trade for keeping the hot path
  free of a per-run file read.
- **Recompile drift.** After an on-phone reauth, the live token on the phone is
  newer than the `SPOTIFY_REFRESH_TOKEN` 1Password secret. **Recompiling
  `Shazam → Spotify` from Cherri will overwrite the fresh token with the stale
  one** — so after any recompile, re-paste the current token (or update the
  1Password secret first). Recompiles are rare.

### Test matrix (run before 2026-07-20)

1. **Valid token** → silent refresh, song added to playlist.
2. **Corrupted token** → hand-edit the `RefreshToken` field to garbage; rerun →
   song queued to Receptor + "run Spotify Reauth" notice.
3. **Reauth flow** → run `Spotify Reauth` (Safari opens), approve, copy the
   redirect URL, run it again, confirm a token lands on the clipboard; paste into
   `Shazam → Spotify`; rerun case 1 succeeds.
