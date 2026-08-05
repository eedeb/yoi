#!/usr/bin/env python3
"""Pull the four photographs out of YOIBrochure.pdf into Photos/.

The brochure is stored as flattened full-page rasters, so the photographs are
not separate embedded images — they have to be cut out of the composited page.
Each one is also feathered into the paper by the layout, so the crops below sit
just inside the solid part of the picture; the soft edge is a brochure device,
not part of the photograph.

    python3 tools/extract-photos.py

Requires: pymupdf, pillow, numpy.
"""
import pathlib

import fitz
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "Photos"

# The page rasters are 1639px across a 792pt page. Rendering at exactly that
# scale copies pixels 1:1 instead of resampling them.
SCALE = 1639 / 792.0

# page number, region of the page in points, then the solid rectangle inside
# that render in pixels. `circle` masks the crop to a disc for the one
# photograph the brochure prints round.
PHOTOS = [
    dict(name="children-waving", page=0, region=(0, 30, 285, 225),
         solid=(55, 45, 512, 358),
         alt="A group of children outdoors, one of them waving at the camera."),
    dict(name="clinic-visit", page=0, region=(510, 30, 792, 215),
         solid=(55, 42, 525, 338),
         alt="A doctor kneeling to examine a small child lying on a mat while "
             "nurses in pink uniforms assist."),
    dict(name="children-listening", page=0, region=(55, 375, 265, 620),
         solid=(20, 81, 340, 401), circle=True,
         alt="A young child with her hands over her ears, standing in a crowd "
             "of other children."),
    dict(name="supplies-delivered", page=1, region=(272, 248, 512, 348),
         solid=(35, 24, 478, 180),
         alt="Clinic staff and a doctor gathered around a large carton of "
             "supplies being handed over."),
]


def render(doc, page, region):
    pix = doc[page].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), clip=fitz.Rect(*region))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def mask_to_circle(im):
    """Cut the crop down to the disc the brochure prints, on transparency.

    Keeping the round crop keeps the children at the edges of the frame, which
    a rectangular crop of the same picture would lose.
    """
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w]
    cy, cx = (h - 1) / 2, (w - 1) / 2
    r = min(w, h) / 2
    dist = np.hypot(xx - cx, yy - cy)
    # 1.5px of feather so the edge is not stair-stepped
    alpha = np.clip((r - 1 - dist) / 1.5 + 1, 0, 1) * 255
    out = np.dstack([np.asarray(im), alpha.astype(np.uint8)])
    return Image.fromarray(out)


def main():
    doc = fitz.open(ROOT / "YOIBrochure.pdf")
    OUT.mkdir(exist_ok=True)

    for p in PHOTOS:
        im = render(doc, p["page"], p["region"]).crop(p["solid"])
        if p.get("circle"):
            im = mask_to_circle(im)
            im.save(OUT / f"{p['name']}.png")
            print(f"{p['name']}.png", im.size)
        else:
            im.save(OUT / f"{p['name']}.jpg", quality=88, optimize=True,
                    progressive=True)
            print(f"{p['name']}.jpg", im.size)


if __name__ == "__main__":
    main()
