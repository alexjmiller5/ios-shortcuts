# Spotify Reauth — Design Spec

**Date:** 2026-06-26
**Status:** Approved, implementing

## Problem

Starting **July 20, 2026**, Spotify refresh tokens expire after six months. Once
expired, a refresh attempt returns `invalid_grant`, and the app must discard the
token and send the user back through the sign-in flow.

Today, the `Shazam → Spotify` shortcut bakes the refresh token into the compiled
`.shortcut` at compile time (`compile-shortcut.sh` runs `op inject` to substitute
`<<secret:SPOTIFY_REFRESH_TOKEN>>`). When that token expires, the shortcut's
refresh call silently returns an empty access token and the run fails downstream
with no useful signal. There is also no on-device way to obtain a replacement
token.

## Goals

- Detect refresh failure (`invalid_grant` / empty access token) and fail loudly
  and usefully instead of silently.
- Never lose the Shazam'd song when the token is expired — queue it to Receptor.
- Make reauthorization possible **entirely from iPhone**, by pasting the OAuth
  redirect URL — no Mac required.
- Keep the hot path fast: the refresh token stays **baked into the shortcut** (no
  per-run file read / `getFile` dependency).

## Non-goals

- Automatic, hands-off token persistence on device. (Rejected `getFile`/`saveFile`
  to keep the main shortcut dependency-free and fast. Consequence: the new token
  is pasted into the shortcut by hand — see Caveats.)
- PKCE. The standard Authorization Code flow (with embedded client secret) is
  sufficient and avoids any SHA256/code-challenge work.

## Architecture

Two shortcuts:

### 1. `Shazam → Spotify` (existing, edited)

Hot path is unchanged for performance. The refresh token remains baked in via
`<<secret:SPOTIFY_REFRESH_TOKEN>>`.

Flow:

1. Shazam → `Song`, `Artist` (locked into variables first).
2. `formRequest` token refresh (`grant_type=refresh_token`) using the baked-in
   refresh token + client id/secret.
3. Convert the access token to text and check it (per the CLAUDE.md conditional
   pattern). **If empty / `invalid_grant`:**
   - Queue the song to Receptor so it is never lost:
     `"Spotify token expired - couldn't add {Song} by {Artist} to the Shazam
     playlist. Run the Spotify Reauth shortcut, paste the new refresh token into
     Shazam → Spotify, then add this song manually $ low priority task"`
   - `show()` a short "token expired — run Spotify Reauth" notice and `stop()`.
   - The expired token is discarded and **never retried** (satisfies Spotify's
     requirement).
4. Otherwise continue with the existing search → add-to-playlist logic using the
   fresh access token.

### 2. `Spotify Reauth` (new — `miscellaneous/spotify_reauth.cherri`)

Run on demand (~2×/year) to mint a new refresh token. **Two-run, clipboard-driven
flow** — iOS foregrounds an in-shortcut `prompt` the instant `openURL` opens
Safari, so a single-run paste prompt pops over the user before they've approved.
Splitting across two runs and handing the redirect URL over via the clipboard
avoids any blocking modal during the Safari step.

The shortcut tells the two runs apart by reading the clipboard up front and
checking for a `code=…`:

- `clipboard = getClipboard()`; `matchText("code=([^&]+)", clipboard)` +
  `getMatchGroup(matches, 1)` → `Code`.

**Run 1 (no `Code` on clipboard):**

1. `alert()` with instructions ("approve, copy the URL, run again").
2. `openURL()` → Spotify authorize page (`response_type=code`,
   `scope=playlist-modify-public playlist-modify-private`,
   `redirect_uri=http://127.0.0.1:8080/callback`) — **last action**, so nothing
   pops over Safari. `stop()`.
3. User approves, lands on `http://127.0.0.1:8080/callback?code=…` (Safari can't
   load it — nothing's listening — but the URL stays in the address bar), copies
   it, returns to Shortcuts.

**Run 2 (`Code` present on clipboard):**

4. `formRequest` token exchange (`grant_type=authorization_code`, the code, the
   redirect URI, client id/secret) → new `refresh_token`.
   - If the response has no refresh token → `show()` the error description +
     `stop()`.
5. `setClipboard()` the new refresh token + `show()`: "copied — paste into the
   RefreshToken field of Shazam → Spotify."

Redirect URI uses the `http://127.0.0.1` loopback form: Spotify allows it but
rejects `localhost`, and requires HTTPS for non-loopback URIs.

## Config / shared values

- New constant in `constants.txt`:
  `SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080/callback` (used by both shortcuts via
  `<<constant:SPOTIFY_REDIRECT_URI>>`).
- `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` (1Password secrets) are baked
  into the reauth shortcut; the main shortcut already uses them.
- `SPOTIFY_REFRESH_TOKEN` secret continues to seed the main shortcut at compile.

## Error handling

- `invalid_grant` / empty access token → Receptor fallback + notice, no retry.
- Search / add failures keep the existing fallbacks (Receptor task, error
  `show()`).
- Reauth: missing `code` in pasted URL, or a failed exchange → clear `show()` +
  `stop()`.

## Caveats (documented in README)

- **Manual paste on expiry.** A running shortcut can't rewrite its own baked-in
  text value, so the new refresh token is pasted into the main shortcut's
  `RefreshToken` text action by hand in the Shortcuts editor (doable on iPhone).
  This is the trade for avoiding `getFile`.
- **Repo/device drift.** The live token on the phone and the Cherri source (via
  the 1Password `SPOTIFY_REFRESH_TOKEN` secret) can diverge. After an on-phone
  reauth, a later recompile from Cherri overwrites the fresh token with the stale
  1Password one. Resolution: after any recompile of the main shortcut, re-paste
  the current token (recompiles are rare), or also update the 1Password secret.

## Testing

Cherri shortcuts can't be unit-tested. Verification:

- `compile-shortcut.sh` compiles both files cleanly.
- Manual on-device test matrix (in README):
  1. **Valid token** → silent refresh, song added.
  2. **Corrupted/expired token** (hand-edit the RefreshToken field to garbage) →
     song queued to Receptor + "run Spotify Reauth" notice.
  3. **Reauth flow** → authorize, paste redirect URL, new token copied to
     clipboard; paste into main shortcut; rerun case 1 succeeds.

## Implementation-time validations (not blockers)

- `openURL → prompt` sequencing on real hardware (alert-gate vs. clipboard read).
- Glyph names compile (`shazam` for main, `key` for reauth).

## One-time manual setup (README)

1. Spotify dashboard → add redirect URI `http://127.0.0.1:8080/callback`.
2. Ensure 1Password secrets exist: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`,
   `SPOTIFY_SHAZAM_PLAYLIST_ID`, `SPOTIFY_REFRESH_TOKEN`.
