# Neuton's Macro - pack gallery

The packs you see in Neuton's Macro → **📦 Sharing hub → Gallery**. The app reads
[`index.json`](index.json) from this repository; there is no server.

## Getting a pack

Open the Sharing hub, go to **Gallery** and click **Load**. Pick a pack and press **Get it**. The app downloads it,
checks its size and SHA-256 against `index.json`, and shows the **🛡 What it can do** card before anything is
installed. A pack's triggers stay switched off until you trust it.

## Adding your pack

1. Make the pack in the app: **Sharing hub → Packs → Make a pack**. Webhooks, tokens, e-mails and user names are
   taken out when the pack is made; the person installing it is asked for their own.
2. Fork this repository and run, from its folder:

   ```
   python tools/add_pack.py path/to/your-pack.nmpack [path/to/preview.png]
   ```

   It copies the pack to `packs/<id>/`, works out its size and SHA-256 and adds (or updates) its entry in
   `index.json`. The preview picture is optional (PNG or JPG, at most 4 MB).
3. Open a pull request. Every pack is opened and checked by hand before it is merged.

A new version of a pack you already have here: run the same command with the new file. People who installed the
older one see **update!** in the gallery and can go back to the version before.

### What isn't accepted

* Anything that cheats in an online game, gets round an anti-cheat, or breaks a game's or a site's rules.
* Packs that run programs, write files or send messages without saying why in their description.
* Packs with someone's webhook, token, password, e-mail or name still in them.
* Packs bigger than 80 MB.

## index.json

```json
{"format": 1,
 "packs": [{"id": "farm-kit", "name": "Farm Kit", "version": "1.2", "author": "someone", "game": "Some game",
            "tags": ["farming"], "about": "What it does", "file": "packs/farm-kit/farm-kit-1.2.nmpack",
            "sha256": "<64 hex characters>", "size": 12345, "preview": "packs/farm-kit/preview.png",
            "signed": false, "updated": "2026-11-09", "changes": ["What changed in this version"]}]}
```

`file` and `preview` are paths inside this repository. The app refuses entries whose path leaves it and any
download whose size or SHA-256 differs from the entry.
