#!/usr/bin/env python3
"""Regenerate assets/ from the logo artwork inside YOIBrochure.pdf.

The brochure's front panel carries the only clean copy of the YOI lockup we
have. It is a raster, printed over a soft cream-to-white vignette, so it can't
just be cropped out — the background has to be estimated and divided away.

    python3 tools/extract-logo.py

Requires: pymupdf, pillow, numpy.
"""
import pathlib

import fitz
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# The brochure page is built from stacked full-page layers; this is the one the
# logo is painted on, and this is the rectangle the lockup occupies inside it.
LOGO_LAYER_XREF = 41
REGION = (980, 730, 1639, 1275)

# REGION is deliberately loose so the background estimator has paper to work
# with on all four sides, which means it also catches the "…AND OTHER REGIONS."
# caption printed above the lockup. Everything above this row is discarded
# before cropping. (Row is relative to REGION; the caption ends well above it.)
CONTENT_TOP = 120

# The stethoscope tube runs out of the Y and down into the wordmark, so the
# standalone mark can't be a plain crop — the tube is painted out instead.
# Coordinates are relative to REGION.
TUBE_BELOW = 356
TUBE_LEFT_X, TUBE_LEFT_Y = 217, 318


def dilate(a, radius):
    """Grey dilation via repeated 1px max-shifts — approximates a max filter."""
    out = a.copy()
    for _ in range(radius):
        for axis in (0, 1):
            s = np.roll(out, 1, axis=axis)
            t = np.roll(out, -1, axis=axis)
            idx = [slice(None)] * out.ndim
            idx[axis] = 0
            s[tuple(idx)] = out[tuple(idx)]
            idx[axis] = -1
            t[tuple(idx)] = out[tuple(idx)]
            out = np.maximum(out, np.maximum(s, t))
    return out


def box_blur(a, radius):
    pad = np.pad(a, ((radius, radius), (radius, radius), (0, 0)), mode="edge")
    c = np.cumsum(np.cumsum(pad, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0), (0, 0)))
    k = 2 * radius + 1
    h, w = a.shape[:2]
    return (c[k:k + h, k:k + w] - c[0:h, k:k + w]
            - c[k:k + h, 0:w] + c[0:h, 0:w]) / (k * k)


def key(img, dil=140, blur=30, floor=0.14):
    """Lift dark artwork off a light, unevenly lit ground.

    The logo is always darker than the paper behind it, so a wide dilation
    recovers the local paper colour; alpha is how far each pixel falls below
    it. `floor` discards the few percent of residual alpha left by paper
    texture — without it the exported PNG carries a faint rectangular haze
    that shows up as a pale box wherever the logo sits on a tinted surface.
    """
    px = np.asarray(img.convert("RGB")).astype(np.float64)
    bg = np.maximum(box_blur(dilate(px, dil), blur), 1.0)

    alpha = 1.0 - np.clip(px / bg, 0, 1).min(axis=2)
    alpha = np.clip((alpha - floor) / (1 - floor), 0, 1)

    a3 = alpha[:, :, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        col = np.clip(np.where(a3 > 0.004, (px - (1 - a3) * bg) / np.maximum(a3, 1e-6), 0), 0, 255)

    return Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8))


def autocrop(im, thresh=25, pad=3):
    """Crop to the artwork, ignoring stray single-pixel specks at the edges."""
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > thresh)
    return im.crop((max(int(xs.min()) - pad, 0), max(int(ys.min()) - pad, 0),
                    min(int(xs.max()) + 1 + pad, im.width),
                    min(int(ys.max()) + 1 + pad, im.height)))


def drop_specks(im, min_px):
    """Erase connected blobs smaller than min_px.

    Painting out the stethoscope leaves a short orphaned stub of tube beside
    the Y that no sane rectangle can remove without clipping the letter, so it
    is dropped by size instead. The mark's real parts are all >9000px.
    """
    from collections import deque

    a = np.asarray(im).copy()
    solid = a[:, :, 3] > 25
    h, w = solid.shape
    seen = np.zeros((h, w), bool)
    kill = np.zeros((h, w), bool)
    for y0, x0 in zip(*np.where(solid)):
        if seen[y0, x0]:
            continue
        q, blob = deque([(y0, x0)]), []
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            blob.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and solid[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(blob) < min_px:
            ys, xs = zip(*blob)
            kill[ys, xs] = True

    # Take the blob's antialiased fringe with it, but never touch a kept shape.
    grown = dilate(kill[:, :, None].astype(np.uint8), 3)[:, :, 0].astype(bool)
    a[grown & ~(solid & ~kill), 3] = 0
    return Image.fromarray(a)


def icon(mark, size, pad=0.06):
    """Square app icon: the mark centred on the site's paper colour."""
    c = Image.new("RGBA", (size, size), (234, 231, 220, 255))
    w = int(size * (1 - 2 * pad))
    m = mark.resize((w, round(w * mark.height / mark.width)), Image.LANCZOS)
    c.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
    return c


def main():
    doc = fitz.open(ROOT / "YOIBrochure.pdf")
    layer = Image.open(__import__("io").BytesIO(
        doc.extract_image(LOGO_LAYER_XREF)["image"])).convert("RGB")

    keyed = key(layer.crop(REGION))
    OUT.mkdir(exist_ok=True)

    def below_caption(im):
        return im.crop((0, CONTENT_TOP, im.width, im.height))

    autocrop(below_caption(keyed)).save(OUT / "yoi-logo.png")

    a = np.asarray(keyed).copy()
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    a[(yy >= TUBE_BELOW) | ((xx < TUBE_LEFT_X) & (yy > TUBE_LEFT_Y)), 3] = 0
    mark = autocrop(drop_specks(below_caption(Image.fromarray(a)), min_px=400))
    mark.save(OUT / "yoi-mark.png")

    icon(mark, 180).convert("RGB").save(OUT / "apple-touch-icon.png")
    icon(mark, 64).save(OUT / "favicon.png")

    for f in ("yoi-logo.png", "yoi-mark.png", "apple-touch-icon.png", "favicon.png"):
        print(f, Image.open(OUT / f).size)


if __name__ == "__main__":
    main()
