"""Adds a Neuton's Macro pack (.nmpack) to this gallery: copies it to packs/<id>/, works out its size and SHA-256 and
adds or updates its entry in index.json. Uses only Python's standard library.

    python tools/add_pack.py path/to/pack.nmpack [path/to/preview.png]
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.json")
MAX_PACK = 80 * 1024 * 1024
MAX_PREVIEW = 4 * 1024 * 1024
MAX_MANIFEST = 2 * 1024 * 1024


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")
    return s[:48] or "pack"


def safe_version(text):
    v = re.sub(r"[^0-9A-Za-z.]+", "-", str(text or "1.0")).strip("-.")
    return v[:24] or "1.0"


def changes_of(manifest, version):
    """The notes the pack's changelog has for this version (a list of short lines)."""
    out = []
    for c in manifest.get("changelog") or []:
        if isinstance(c, dict) and safe_version(c.get("version")) == version:
            notes = c.get("notes") or ""
            out += [str(n) for n in notes] if isinstance(notes, list) else [ln for ln in str(notes).splitlines() if ln]
        elif isinstance(c, str):
            out.append(c)
    return out[:20]


def read_manifest(path):
    with zipfile.ZipFile(path) as z:
        info = z.getinfo("manifest.json")
        if info.file_size > MAX_MANIFEST:
            raise SystemExit("manifest.json is too big")
        m = json.loads(z.read("manifest.json").decode("utf-8"))
        signed = "manifest.sig" in z.namelist()
    if not isinstance(m, dict) or m.get("format") != 1:
        raise SystemExit("This isn't a Neuton's Macro pack (format 1)")
    return m, signed


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    pack = argv[1]
    preview = argv[2] if len(argv) > 2 else ""
    size = os.path.getsize(pack)
    if size > MAX_PACK:
        raise SystemExit("The pack is bigger than 80 MB")
    m, signed = read_manifest(pack)
    pid = slug(m.get("id") or m.get("name"))
    version = safe_version(m.get("version"))
    folder = os.path.join(ROOT, "packs", pid)
    os.makedirs(folder, exist_ok=True)
    name = f"{pid}-{version}.nmpack"
    shutil.copyfile(pack, os.path.join(folder, name))
    data = open(os.path.join(folder, name), "rb").read()
    entry = {"id": pid, "name": str(m.get("name") or pid), "version": version, "author": str(m.get("author") or ""),
             "game": str(m.get("game") or ""), "tags": [str(t) for t in m.get("tags") or []][:12],
             "about": str(m.get("about") or ""), "file": f"packs/{pid}/{name}",
             "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "preview": "", "signed": signed,
             "updated": datetime.date.today().isoformat(),
             "changes": changes_of(m, version)}
    if preview:
        ext = os.path.splitext(preview)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            raise SystemExit("The preview must be a .png or .jpg")
        if os.path.getsize(preview) > MAX_PREVIEW:
            raise SystemExit("The preview is bigger than 4 MB")
        shutil.copyfile(preview, os.path.join(folder, "preview" + ext))
        entry["preview"] = f"packs/{pid}/preview{ext}"
    else:
        old = [f for f in os.listdir(folder) if f.startswith("preview.")]
        if old:
            entry["preview"] = f"packs/{pid}/{old[0]}"
    index = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else {"format": 1, "packs": []}
    index["packs"] = [e for e in index.get("packs") or [] if slug(e.get("id")) != pid] + [entry]
    index["packs"].sort(key=lambda e: str(e.get("name", "")).lower())
    with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"Added {entry['name']} {version} ({len(data)} bytes, sha256 {entry['sha256'][:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
