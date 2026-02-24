# iOS Shortcuts

## About This Repo

- The folder structure of the shortcuts will mirror the structure of the folder in my iCloud Shortcuts apps
- The shortcuts will be written in [Cherri](https://cherrilang.org/)

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

The compile script expands these to `op://Personal/NAME/credential` and uses the 1Password CLI (`op inject`) to substitute actual values.

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
