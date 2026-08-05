# Youth Outreach International — website

Static site for Youth Outreach International, a 501(c)(3) ministry based in
Lancaster, PA. No build step, no dependencies, no framework. Plain HTML and CSS.

Live at <https://yoi.eedeb.dev>

## Structure

```
index.html              About Us — serves as the homepage
news.html               Field dispatches (Haiti, Kenya)
get-involved.html       Programs, cost breakdown, contact
gallery.html            Photo carousel
site.css                All styling for every page
site.js                 Copyright year, scroll reveals, gallery carousel
YOIBrochure.pdf         The printed brochure; linked from three pages, and the
                        source of record for the copy, the logo and the photos
assets/                 Logo artwork and icons (generated — see below)
Photos/                 Field photographs (generated — see below)
tools/extract-logo.py   Regenerates assets/ from the brochure
tools/extract-photos.py Regenerates Photos/ from the brochure
.nojekyll               Tells GitHub Pages to serve the files as-is
```

The pages are flat in one directory. `site.css` and `site.js` are shared by all
of them, so a change to either affects the whole site.

## Logo assets

There is no vector original. The only clean copy of the lockup is a raster on
the brochure's front panel, printed over a soft cream vignette, so it can't
simply be cropped out — the background is estimated and divided away.
`tools/extract-logo.py` does that and writes:

```
assets/yoi-logo.png         full stacked lockup (mark + wordmark)
assets/yoi-mark.png         the YOI mark alone, stethoscope tube painted out
assets/favicon.png          64px icon
assets/apple-touch-icon.png 180px icon
assets/yoi-header.png       the old site's horizontal header banner, unused
```

Rerun it with `python3 tools/extract-logo.py` (needs pymupdf, pillow, numpy).

**The keyed artwork only works on a light surface.** Alpha was recovered by
measuring how far each pixel falls below the paper behind it, which means the
logo's dark gradient is partly carried in the alpha channel rather than the
colour. On parchment it composites exactly; on `--espresso` the letterforms
would wash out. Do not put `yoi-logo.png` or `yoi-mark.png` on a dark band.

## Photographs

The brochure carries four photographs and they are the only ones we have.
Like the logo they are not separate embedded files — the brochure is stored as
flattened full-page rasters — so `tools/extract-photos.py` cuts them out of the
composited page at 1:1 pixels and writes `Photos/`:

```
Photos/children-waving.jpg      457 × 313
Photos/clinic-visit.jpg         470 × 296
Photos/children-listening.png   320 × 320, circular, transparent corners
Photos/supplies-delivered.jpg   443 × 156
```

Two things about the crops. Each photograph is feathered into the paper by the
layout, so the rectangles in the script sit just inside the solid part of the
picture — the soft edge is a brochure device, not part of the photograph, and
including it would put a pale halo around every slide. And the third is printed
as a circle; it is kept round, on transparency, because a rectangular crop of
the same picture loses the children at the edges of the frame.

They cap out around 450px wide. The brochure's own rasters are 1639px across an
11-inch sheet, roughly 150dpi, so there is no more detail to recover — that is
the ceiling, not a setting. If the original photographs ever turn up, replace
the files and delete the script.

## Local preview

Open `index.html` directly in a browser, or run a local server so paths behave
exactly as they do in production:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy

### GitHub Pages

Push to `main`, then set Settings → Pages → Source to `main` / `/ (root)`. Every
path in the markup is relative, so the site works both at `user.github.io/yoi/`
and at a custom domain. `.nojekyll` keeps Pages from running the files through
Jekyll; leave it in place.

### Copying to a server

```bash
rsync -av --delete \
  --exclude '.git' --exclude '.gitignore' --exclude 'README.md' \
  --exclude 'tools' \
  ./ user@server:/var/www/yoi/
```

That deployment sits behind Cloudflare, which caches CSS and JS aggressively. After
deploying a change to `site.css` or `site.js`, either purge the Cloudflare cache
or bump the version string in every page's `<link>` and `<script>` tags:

```html
<link href="site.css?v=5" rel="stylesheet">
<script src="site.js?v=5"></script>
```

Bumping the version is the more reliable of the two — it makes the URL new, so
nothing anywhere can serve a stale copy.

## Design notes

Typefaces are loaded from Google Fonts: Bricolage Grotesque (headings),
Newsreader (body text), IBM Plex Mono (labels and small caps).

Colours are defined once as custom properties at the top of `site.css` and were
sampled directly off the printed brochure: parchment (`--paper`), the wordmark's
taupe, espresso for text and dark bands, and the logo's orange as the single
accent. The brochure is a two-colour piece and the site follows it — there is no
second hue, only a warm ramp (`--flame-deep`, `--clay`, `--ink-2`) to tell the
three programme areas apart.

`--flame` is the orange exactly as printed. It is too light to read as small
text on parchment, so anything typographic uses `--flame-deep`; `--flame` is for
rules, the cost figures on the dark band, and other large or graphic marks.

Every section headline sits over a short orange rule, which is the brochure's
signature. It comes from one CSS rule covering `.hero h1`, `.pagehead h1` and
`.section-head h2` — no markup needed.

`.rise` elements fade in on scroll. They only start hidden if JavaScript is
confirmed present — an inline script in each `<head>` adds a `js` class to
`<html>`, and the hiding rule is scoped to `.js .rise`. If `site.js` fails to
load, content still renders. Do not remove that inline script.

The gallery carousel is a native scroll-snapping strip, not a slideshow. CSS
does the snapping and `site.js` only scrolls the strip and keeps the dots and
counter in step with wherever it actually is, so swiping, arrow keys and the
buttons can never disagree about which photo is showing. With JavaScript off
the strip still scrolls and swipes; `.carousel-nav` is scoped to `.js` and
simply never appears. Stepping between neighbouring photos glides, but wrapping
past either end jumps, since animating that would rewind through every slide in
between.

The country marquee on the homepage duplicates its list in the markup; both
copies translate left by 100% of their own width, which makes the loop seamless.
The second copy is `aria-hidden` so screen readers announce each country once.
Speed is set by `--marquee-duration` and steps down at narrower breakpoints so
the apparent motion stays constant.

All layouts collapse to a single column at 820px. Header restructures at 760px.
Typography steps down at 560px and again at 360px.

## Outstanding

Content that still needs resolving before this is fully accurate:

- **Gallery photographs** — the page is built, but the only photographs we have
  are the four lifted out of the brochure, and they are small. The original
  gallery from the old site has not been recovered from the Wayback Machine.
  None of the four is captioned in the brochure, so the captions on the page
  describe what is visible and claim no country or date; if anyone can identify
  the places or the people, the captions should say so.
- **Sixteenth country** — the brochure lists fifteen: Benin, Congo, Haiti,
  Indonesia, Ghana, Guatemala, Kenya, Moldova, Romania, Rwanda, Sierra Leone,
  Sudan, Uganda, United States and Zambia. The homepage marquee carries a
  sixteenth, Malawi, flagged "Newest", and the headline and footer both say
  sixteen. Malawi appears in no source we have. Confirm it or drop it and change
  the count back to fifteen in `index.html`.
- **Cost figures** — the amounts on get-involved.html ($15, $10, $20, $20) match
  the brochure exactly, but the brochure is undated. Verify against current
  field costs.
- **News dates** — both dispatches are undated. Commented markup marks where a
  date goes in each article. Note the dispatches cover Haiti and Kenya, while
  the brochure's front panel names Gulu, Darfur, Freetown and Guatemala as the
  active fields; the homepage now lists the latter.
- **Plumpy'Nut video** — the original was Flash and is unplayable. A placeholder
  block on index.html marks where a YouTube or Vimeo embed should go.
- **Verify before publishing** — the 501(c)(3) registration, the PayPal button
  (`3YQ8JTTSHS934`), the phone number and the AOL address all date to 2021 or
  earlier and should be confirmed live.
