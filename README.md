# Youth Outreach International — website

Static site for Youth Outreach International, a 501(c)(3) ministry based in
Lancaster, PA. No build step, no dependencies, no framework. Plain HTML and CSS.

Live at <https://yoi.eedeb.dev>

## Structure

```
index.html          About Us — serves as the homepage
news.html           Field dispatches (Haiti, Kenya)
get-involved.html   Programs, cost breakdown, contact
gallery.html        NOT YET BUILT — see "Outstanding" below
site.css            All styling for every page
site.js             Scroll reveals + auto-updating copyright year
YOIBrochure.pdf     Linked from index.html and get-involved.html
```

Everything is flat in one directory. `site.css` and `site.js` are shared by all
pages, so a change to either affects the whole site.

## Local preview

Open `index.html` directly in a browser, or run a local server so paths behave
exactly as they do in production:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy

Copy the tracked files to the web root:

```bash
rsync -av --delete \
  --exclude '.git' --exclude '.gitignore' --exclude 'README.md' \
  ./ user@server:/var/www/yoi/
```

The site sits behind Cloudflare, which caches CSS and JS aggressively. After
deploying a change to `site.css` or `site.js`, either purge the Cloudflare cache
or bump the version string in every page's `<link>` and `<script>` tags:

```html
<link href="site.css?v=4" rel="stylesheet">
<script src="site.js?v=4"></script>
```

Bumping the version is the more reliable of the two — it makes the URL new, so
nothing anywhere can serve a stale copy.

## Design notes

Typefaces are loaded from Google Fonts: Bricolage Grotesque (headings),
Newsreader (body text), IBM Plex Mono (labels and small caps).

Colours are defined once as custom properties at the top of `site.css`. The
palette derives from the original 2009 site's khaki and brown, sharpened into
deep pine green, water blue and ochre. One accent colour per programme area:
green for clinics, blue for water, ochre for food.

`.rise` elements fade in on scroll. They only start hidden if JavaScript is
confirmed present — an inline script in each `<head>` adds a `js` class to
`<html>`, and the hiding rule is scoped to `.js .rise`. If `site.js` fails to
load, content still renders. Do not remove that inline script.

The country marquee on the homepage duplicates its list in the markup; both
copies translate left by 100% of their own width, which makes the loop seamless.
The second copy is `aria-hidden` so screen readers announce each country once.
Speed is set by `--marquee-duration` and steps down at narrower breakpoints so
the apparent motion stays constant.

All layouts collapse to a single column at 820px. Header restructures at 760px.
Typography steps down at 560px and again at 360px.

## Outstanding

Content that still needs resolving before this is fully accurate:

- **Gallery page** — not yet rebuilt. Needs the original page recovered from the
  Wayback Machine, plus the photographs.
- **Conflicting address** — the old Get Involved page listed 146 East Main
  Street, Leola, PA 17540 in its body copy, while its own footer and every other
  page listed 43 Breeze Way, Lancaster, PA 17602. Lancaster is used throughout.
  Confirm which is correct; this is the address donors mail cheques to.
- **Cost figures** — the amounts on get-involved.html ($15, $10, $20, $20) were
  published around 2019 and should be verified against current field costs.
- **News dates** — both dispatches are undated. Commented markup marks where a
  date goes in each article.
- **Plumpy'Nut video** — the original was Flash and is unplayable. A placeholder
  block on index.html marks where a YouTube or Vimeo embed should go.
- **Verify before publishing** — the 501(c)(3) registration, the PayPal button
  (`3YQ8JTTSHS934`), the phone number and the AOL address all date to 2021 or
  earlier and should be confirmed live.
