#!/usr/bin/env python3
"""Make everything in Photos/ safe and fit for a public web page.

    python3 tools/prepare-photos.py

Photos arrive straight off phones, so as they come they are not fit to publish:

  * Most carry GPS coordinates. On this site that can mean the exact location
    of a school or a family's home. Every photo is re-encoded with all of its
    metadata dropped, which is the only reliable way to be rid of it.
  * iPhones save HEIC, which Chrome and Firefox cannot display at all.
  * Originals run to 4032px and several megabytes; the gallery never shows one
    more than about 1000 CSS pixels across.
  * Phone screenshots of portrait photos come letterboxed in black bars.
  * iPhone colour is Display P3, which browsers read as sRGB unless it is
    converted, so photos come out flat if the profile is just thrown away.

Each photo is turned upright, trimmed of letterboxing, converted to sRGB,
shrunk to fit MAX_EDGE, and written back as a metadata-free JPEG (or PNG, if it
really uses transparency). A file that has already been through this — small
enough, no metadata, web format — is left alone, so it is safe to run on every
push. The Photos workflow does exactly that.

Requires: pillow, pillow-heif.
"""
import io
import os
import pathlib
import sys

from PIL import Image, ImageCms, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:  # still useful for everything that isn't HEIC
    pillow_heif = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "Photos"

MAX_EDGE = 1800
JPEG_QUALITY = 80
WEB = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
CONVERT = {".heic", ".heif", ".tif", ".tiff", ".bmp"}

# Rows or columns darker than this, all the way across, count as letterbox.
BAR_LEVEL = 24
# ...but only bother if the bars are at least this share of the picture, so a
# photo that simply has a dark edge keeps it.
BAR_MIN_SHARE = 0.02


def needs_work(path):
    ext = path.suffix.lower()
    if ext in CONVERT:
        return True
    if ext not in WEB:
        return False
    with Image.open(path) as im:
        if max(im.size) > MAX_EDGE:
            return True
        if im.getexif() or im.info.get("icc_profile") or im.info.get("exif"):
            return True
        if ext == ".png" and not has_alpha(im):
            return True  # a photo saved as PNG; a JPEG is a fraction the size
    return False


def has_alpha(im):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA").getextrema()[3][0] < 255
    return False


def to_srgb(im):
    icc = im.info.get("icc_profile")
    if not icc:
        return im
    try:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        dst = ImageCms.createProfile("sRGB")
        mode = "RGBA" if im.mode in ("RGBA", "LA") else "RGB"
        return ImageCms.profileToProfile(im.convert(mode), src, dst, outputMode=mode)
    except (ImageCms.PyCMSError, OSError):
        return im


def trim_letterbox(im):
    """Cut away solid black bars, as phone screenshots of photos have."""
    mask = im.convert("L").point(lambda v: 255 if v > BAR_LEVEL else 0)
    box = mask.getbbox()
    if not box:
        return im
    l, t, r, b = box
    w, h = im.size
    if max(l, w - r) / w < BAR_MIN_SHARE and max(t, h - b) / h < BAR_MIN_SHARE:
        return im
    return im.crop(box)


def prepare(im):
    """Upright, unletterboxed, sRGB, sized for the web. Returns a new image."""
    im = ImageOps.exif_transpose(im)
    im = to_srgb(im)
    im = trim_letterbox(im)
    im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    return im


def save_web(im, dest_stem):
    """Write without metadata. Returns the path written."""
    if has_alpha(im):
        out = dest_stem.with_suffix(".png")
        im.convert("RGBA").save(out, optimize=True)
    else:
        out = dest_stem.with_suffix(".jpg")
        im.convert("RGB").save(out, quality=JPEG_QUALITY, optimize=True, progressive=True)
    return out


def same_file(a, b):
    # Compare by identity, not by name: macOS filesystems ignore case, so
    # "photo.JPG" and "photo.jpg" are one file there and two on Linux.
    return a.exists() and b.exists() and os.path.samefile(a, b)


def free_stem(path):
    """The stem to write to, without clobbering a different photo."""
    stem = path.with_suffix("")
    for ext in (".jpg", ".png"):
        clash = stem.with_suffix(ext)
        if clash.exists() and not same_file(clash, path):
            n = 2
            while stem.with_name(f"{stem.name}-{n}").with_suffix(ext).exists():
                n += 1
            return stem.with_name(f"{stem.name}-{n}")
    return stem


def main():
    changed = 0
    for path in sorted(p for p in PHOTOS.rglob("*") if p.is_file()):
        if not needs_work(path):
            continue
        if path.suffix.lower() in {".heic", ".heif"} and pillow_heif is None:
            sys.exit("pillow-heif is needed to convert " + str(path))
        with Image.open(path) as src:
            src.load()
            im = prepare(src)
        out = save_web(im, free_stem(path))
        if not same_file(out, path):
            path.unlink()
        changed += 1
        print(f"  {path.relative_to(ROOT)} -> {out.name} {im.size[0]}x{im.size[1]}")
    print(f"prepare-photos: {changed} photo(s) processed")


if __name__ == "__main__":
    main()
