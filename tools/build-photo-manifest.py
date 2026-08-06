#!/usr/bin/env python3
"""List Photos/ into photos.json.

The gallery reads the Photos folder at page load. On any server with directory
listings switched on it just asks for the folder, but GitHub Pages does not
serve listings, so it needs this file to fall back to.

    python3 tools/build-photo-manifest.py

Nothing outside the standard library. The Photos workflow reruns it on every
push that touches Photos/, so a photo uploaded through the GitHub web interface
turns up in the gallery on its own; run it by hand if you are working locally
and want the manifest to match before you commit.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "Photos"
MANIFEST = ROOT / "photos.json"

SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}


def natural_key(name):
    """Sort the way the gallery does: by name, with numbers read as numbers."""
    parts, digits = [], ""
    for ch in name.lower():
        if ch.isdigit():
            digits += ch
        else:
            if digits:
                parts.append((1, int(digits), ""))
                digits = ""
            parts.append((0, 0, ch))
    if digits:
        parts.append((1, int(digits), ""))
    return parts


def main():
    names = sorted(
        (p.name for p in PHOTOS.iterdir()
         if p.is_file() and p.suffix.lower() in SUFFIXES),
        key=natural_key,
    )
    MANIFEST.write_text(json.dumps(names, indent=2) + "\n")
    print(f"{MANIFEST.name}: {len(names)} photo(s)")
    for n in names:
        print("  " + n)


if __name__ == "__main__":
    main()
