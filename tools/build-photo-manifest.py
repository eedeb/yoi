#!/usr/bin/env python3
"""Index Photos/ into photos.json.

The gallery reads each Photos subfolder at page load. On any server with
directory listings switched on it just asks for the folder, but GitHub Pages
does not serve listings, so it needs this file to fall back to.

    python3 tools/build-photo-manifest.py

The file maps each folder, written exactly as gallery.html names it in
data-photos, to the photos inside:

    { "Photos/Haiti/": ["cover.jpg", "01.jpg", ...], ... }

Nothing outside the standard library. The Photos workflow reruns it on every
push that touches Photos/, so a photo uploaded through the GitHub web interface
turns up in the gallery on its own; run it by hand if you are working locally
and want the manifest to match before you commit.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "Photos"
MANIFEST = ROOT / "photos.json"

SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}


def order(name):
    """Sort the way the gallery does: any cover first, then by name with
    numbers read as numbers, so 2 comes before 10."""
    cover = 0 if re.fullmatch(r"cover\.[^.]+", name, re.I) else 1
    parts = [(0, int(t), "") if t.isdigit() else (1, 0, t)
             for t in re.split(r"(\d+)", name.lower()) if t]
    return (cover, parts)


def photos_in(folder):
    return sorted((p.name for p in folder.iterdir()
                   if p.is_file() and p.suffix.lower() in SUFFIXES), key=order)


def main():
    manifest = {}
    for folder in sorted([PHOTOS, *(p for p in PHOTOS.rglob("*") if p.is_dir())]):
        names = photos_in(folder)
        if names:
            key = folder.relative_to(ROOT).as_posix() + "/"
            manifest[key] = names
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"{MANIFEST.name}: {sum(map(len, manifest.values()))} photo(s)")
    for key, names in manifest.items():
        print(f"  {key}  {len(names)}")


if __name__ == "__main__":
    main()
