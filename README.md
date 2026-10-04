# Youth Outreach International — website

Static site for Youth Outreach International, a 501(c)(3) ministry based in
Lancaster, PA. No build step, no dependencies, no framework. Plain HTML and CSS.

Live at <https://yoi.eedeb.dev>

## Structure

```
index.html              Home: short introduction, how we work, the three ministries
ministries.html         Each ministry's full story, needs, website and photos
history.html            Dr. Niemeyer's story, countries reached, archive photos
news.html               Field dispatches (Haiti, Kenya)
get-involved.html       Ways to help, what a gift covers, contact
gallery.html            Redirect only: old links land on ministries.html
site.css                All styling for every page
site.js                 Copyright year, scroll reveals, gallery carousels
YOIBrochure.pdf         The printed brochure; linked from three pages, and the
                        source of record for the copy and the logo
assets/                 Logo artwork and icons (generated — see below)
Photos/                 The gallery, one folder per section. See below
photos.json             Index of Photos/, for hosts that can't list a directory
tools/extract-logo.py   Regenerates assets/ from the brochure
tools/prepare-photos.py Strips GPS, converts HEIC, resizes. Run before committing
tools/build-photo-manifest.py   Rewrites photos.json from Photos/
.github/workflows/photos.yml    Runs both on every push touching Photos/
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

## The gallery

`Photos/` holds one folder per gallery section:

```
Photos/Grace Life/            Grace Life Bible College, Webuye, Kenya
Photos/Maisha/                Maisha Project, Kenya
Photos/Haiti/                 Institution Puits Jacob, Montrouis, Haiti
Photos/Blast from the Past/   historic photos, clippings and keepsakes
```

They came from the organisation's iCloud shared albums of the same names. The
"Uganda" album was left out on purpose, and the old brochure placeholders are
gone.

**To add a photo, put the file in its folder.** Nothing else. No list to edit,
no markup to touch. Each carousel (three on `ministries.html`, the archive on
`history.html`) names its folder in
`data-photos` and ships empty; `site.js` fills it from whatever is in there.
Remove a file and it's gone; rename files to reorder them, since they sort by
name with numbers read as numbers (so `2` comes before `10`).

**`cover.jpg` is special.** In each ministry folder it is the picture on that
ministry's summary card on the home page, and it always leads the carousel.
Swap a cover by replacing that one file. The covers are the three from the
"Three pictures" album; each is also in its own ministry's album, which is how
they were matched up.

**A new carousel** is a copy of one of the `<div class="carousel" data-carousel>`
blocks pointed at a new folder.

A descriptive filename doubles as alt text: `children-waving.jpg` is announced
as "Children waving". Camera names, bare numbers and random IDs say nothing,
so those fall back to the section and position instead — "Haiti, photo 3 of
17". The imported photos are numbered `01.jpg`, `02.jpg`... in the order they
were taken, so they all read that way.

Past a dozen photos a carousel drops its dots and relies on the "3 / 17"
counter. A dot per photo stopped being usable long before it stopped fitting,
and 88 of them pushed the whole page sideways.

### Photos are cleaned before they are published

Photos straight off a phone are not fit to put on a public page, and
`tools/prepare-photos.py` fixes that for everything in `Photos/`:

- **Location.** Most phone photos carry GPS coordinates; 49 of the imported
  ones did, some of them pointing at schools and homes. Every photo is
  re-encoded with all metadata dropped.
- **Format.** iPhones save HEIC, which Chrome and Firefox cannot display. It is
  converted to JPEG, and so are photos that were saved as PNG.
- **Size.** Originals run to 4032px and several megabytes. They are shrunk to
  1800px on the long edge; the imported albums went from about 300MB to 40MB.
- **Letterboxing.** Phone screenshots of portrait photos come with black bars,
  which are trimmed.
- **Colour.** iPhone photos are Display P3. They are converted to sRGB rather
  than having the profile thrown away, which would leave them looking flat.

Photos it has already prepared are left alone, so it is safe to run any time:

```bash
python3 tools/prepare-photos.py      # needs: pip install pillow pillow-heif
```

The Photos workflow runs it on every push that touches `Photos/`. **But the
workflow only fixes what the site serves, not the history.** A photo uploaded
as-is is still in the commit that added it, GPS and all. To keep a location out
of the repository entirely, run the script before committing.

Four prints in the archive were photographed lying flat and came out sideways,
and one entry was a screenshot of an email; those were rotated and cropped by
hand during the import. Their numbers are 50, 51, 55, 62 and 65 in
`Blast from the Past`.

### How the gallery finds them

A browser cannot read a directory off a static host, so it takes two goes:

1. **Ask the server for the folder.** Any host with directory listings on —
   including `python3 -m http.server` below — answers with a page of links,
   which is always current. Locally this is the whole story: drop a file in,
   reload, there it is.
2. **Fall back to `photos.json`.** GitHub Pages serves no listings and 404s
   that first request, which is harmless but does show up in the network panel.
   `tools/build-photo-manifest.py` writes the file, mapping each folder to its
   photos, and the Photos workflow reruns it after preparing the photos — so a
   photo uploaded through the GitHub web interface appears on its own once the
   action and the Pages deploy finish.

The workflow's own commit cannot set it off again: pushes made with the built-in
`GITHUB_TOKEN` never start new workflow runs, and both scripts would find
nothing to do anyway.

## Local preview

Run a local server rather than opening the files directly — the gallery reads
the `Photos` folder over HTTP and cannot do that from a `file://` page:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

This server lists directories, so the gallery picks up anything you drop into
`Photos/` the moment you reload. Every other page is fine opened directly.

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
  --exclude 'tools' --exclude '.github' \
  ./ user@server:/var/www/yoi/
```

Ship `photos.json` — it is what the gallery falls back to when the host does
not list directories. Run `tools/build-photo-manifest.py` before deploying if
`Photos/` changed, since nothing outside GitHub runs the workflow.

That deployment sits behind Cloudflare, which caches CSS and JS aggressively. After
deploying a change to `site.css` or `site.js`, either purge the Cloudflare cache
or bump the version string in every page's `<link>` and `<script>` tags:

```html
<link href="site.css?v=7" rel="stylesheet">
<script src="site.js?v=7"></script>
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
buttons can never disagree about which photo is showing. Stepping between
neighbouring photos glides, but wrapping past either end jumps, since animating
that would rewind through every slide in between. Note that the jump has to ask
for `behavior: 'instant'` — `'auto'` defers to the CSS `scroll-behavior`, which
is smooth here, so it would animate the very case meant to skip animating.

The gallery is the one page that needs JavaScript, because reading the folder
is what puts the photos there; it says so in a `<noscript>` rather than showing
an empty frame. Everything else on the site still renders without it.

Photos arrive from a folder at any size or shape, so the slide sets a fixed
height and uses `object-fit: contain`. The frame never moves between photos and
nothing shifts as they load, which is also why the images carry no `width` and
`height` attributes — their real dimensions are not known until they arrive and
would not change the layout anyway.

The country marquee on the homepage duplicates its list in the markup; both
copies translate left by 100% of their own width, which makes the loop seamless.
The second copy is `aria-hidden` so screen readers announce each country once.
Speed is set by `--marquee-duration` and steps down at narrower breakpoints so
the apparent motion stays constant.

All layouts collapse to a single column at 820px. Header restructures at 760px.
Typography steps down at 560px and again at 360px.

## Where the copy comes from

The ministry stories, the introduction and the history were rewritten in
October 2026 from an update written by the ministry ("claude update yoi.pdf"),
which also asked for the 96% giving note. The brochure's vision and mission
statements still stand on the home page.

## Outstanding

Content that still needs resolving before this is fully accurate:

- **Puits Jacob's Facebook page** — the update linked it only as
  "facebook.com", which goes to Facebook's front page. Until the real page
  address is known, the button on ministries.html opens a Facebook search for
  the school's name. Replace its `href` (there is a TODO beside it).
- **Grace Life's books** — the update says one place that two containers held
  13,000 books, and another that they held over 23,000. The site uses "more
  than 23,000". Confirm which is right.
- **Project Peanut Butter** — the update calls it "The Peanut Butter Project";
  the DVD in the archive photos is titled "The Story of Project Peanut Butter",
  which is the name the history page uses. Confirm.
- **Sixteenth country** — the brochure lists fifteen countries where YOI
  supported clinics. The history page's list carries a sixteenth, Malawi, which
  came from the old website and appears in no other source (Project Peanut
  Butter does work there). Confirm it, or drop it and say fifteen.
- **News dates** — both dispatches are undated. Commented markup marks where a
  date goes in each article.
- **Verify before publishing** — the 501(c)(3) registration, the PayPal button
  (`3YQ8JTTSHS934`), the phone number and the AOL address all date to 2021 or
  earlier and should be confirmed live.
