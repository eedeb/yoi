(function () {
  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();

  var items = document.querySelectorAll('.rise');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!reduced && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // ---- gallery ----------------------------------------------------------
  // The gallery has no hard-coded list of photos: whatever sits in Photos/ is
  // what shows up. Finding out what sits there takes two goes, because a
  // static host will not let a browser read a directory:
  //
  //   1. Ask the server for the folder. Any host with directory listings on —
  //      including `python3 -m http.server` from the README — answers with a
  //      page of links, which is always current. Drop a file in, reload, done.
  //   2. GitHub Pages has no listings and 404s that request (harmless, but it
  //      does show up in the network panel), so fall back to photos.json.
  //      tools/build-photo-manifest.py writes that file and the Photos
  //      workflow reruns it on every push that touches Photos/.
  //
  // Photos are ordered by filename, numerically, so 2 sorts before 10 and a
  // "01-" style prefix is enough to arrange them.

  var IMAGE = /\.(jpe?g|png|gif|webp|avif|svg)$/i;

  function byName(names) {
    return names.sort(function (a, b) {
      return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
    });
  }

  function fromListing(dir) {
    return fetch(dir).then(function (r) {
      if (!r.ok) throw new Error('no listing');
      return r.text();
    }).then(function (html) {
      var links = new DOMParser().parseFromString(html, 'text/html')
        .querySelectorAll('a[href]');
      var names = [];
      Array.prototype.forEach.call(links, function (a) {
        var href = a.getAttribute('href').split('?')[0].split('#')[0];
        // Skip the parent link and any subfolder; we only want files here.
        if (!href || href.indexOf('/') > -1) return;
        var name = decodeURIComponent(href);
        if (IMAGE.test(name)) names.push(name);
      });
      if (!names.length) throw new Error('listing had no images');
      return names;
    });
  }

  function fromManifest() {
    return fetch('photos.json', { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('no manifest');
      return r.json();
    }).then(function (list) {
      return (list || []).filter(function (n) {
        return typeof n === 'string' && IMAGE.test(n);
      });
    });
  }

  function listPhotos(dir) {
    return fromListing(dir)
      .catch(fromManifest)
      .catch(function () { return []; })
      .then(byName);
  }

  // Filenames double as alt text, so naming a file well is how you describe a
  // photo. "children-waving.jpg" reads as "Children waving"; a camera's
  // "IMG_4821.jpg" reads as itself, which is no worse than nothing.
  function altFor(name) {
    var base = name.replace(/\.[^.]+$/, '')
      .replace(/[-_]+/g, ' ')
      .replace(/^\s*\d+\s+/, '')   // drop an ordering prefix like "03 "
      .trim();
    if (!base) return 'Photograph';
    return base.charAt(0).toUpperCase() + base.slice(1);
  }

  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var track = root.querySelector('.carousel-track');
    if (!track) return;
    var dir = root.getAttribute('data-photos') || 'Photos/';

    // Controls stay out of the way until we know there is something to control
    // — an empty or single-photo folder should not get Previous and Next.
    var nav = root.querySelector('.carousel-nav');
    if (nav) nav.hidden = true;

    listPhotos(dir).then(function (names) {
      var empty = root.querySelector('[data-carousel-empty]');
      if (!names.length) {
        if (empty) empty.hidden = false;
        track.hidden = true;
        return;
      }

      names.forEach(function (name, i) {
        var li = document.createElement('li');
        li.className = 'carousel-slide';
        var img = document.createElement('img');
        img.src = dir + name.split('/').map(encodeURIComponent).join('/');
        img.alt = altFor(name);
        // The first one is what you see on arrival; the rest can wait until
        // they are scrolled towards.
        if (i) img.loading = 'lazy';
        li.appendChild(img);
        track.appendChild(li);
      });

      initCarousel(root, track, names.length);
    });
  });

  // The slides are a native scroll-snapping strip (see site.css). Nothing here
  // moves them; it only scrolls the strip and keeps the dots and counter in
  // step with wherever the strip actually is, so dragging, arrow keys and the
  // buttons can't disagree about which photo is showing.
  function initCarousel(root, track, total) {
    var dotsWrap = root.querySelector('.carousel-dots');
    var count = root.querySelector('.carousel-count');
    var nav = root.querySelector('.carousel-nav');

    // One photo needs no controls; the nav stays hidden.
    if (total < 2) return;
    if (nav) nav.hidden = false;

    var index = 0;
    var dots = [];

    function go(i) {
      var n = (i % total + total) % total;
      // Going off either end wraps. Animating that would rewind through every
      // slide in between, so wraps jump and only ordinary steps glide.
      var wrapped = i < 0 || i >= total;
      // 'instant', not 'auto': 'auto' defers to the CSS scroll-behavior, which
      // is smooth on this track, so it would animate the very cases meant to
      // skip the animation.
      track.scrollTo({
        left: n * track.clientWidth,
        behavior: (reduced || wrapped) ? 'instant' : 'smooth'
      });
    }

    if (dotsWrap) {
      for (var i = 0; i < total; i++) {
        (function (n) {
          var dot = document.createElement('button');
          dot.type = 'button';
          dot.className = 'carousel-dot';
          dot.setAttribute('aria-label', 'Photo ' + (n + 1) + ' of ' + total);
          dot.addEventListener('click', function () { go(n); });
          dotsWrap.appendChild(dot);
          dots.push(dot);
        })(i);
      }
    }

    function sync() {
      var w = track.clientWidth;
      if (!w) return;
      index = Math.max(0, Math.min(total - 1, Math.round(track.scrollLeft / w)));
      dots.forEach(function (dot, i) {
        dot.setAttribute('aria-current', i === index ? 'true' : 'false');
      });
      if (count) count.textContent = (index + 1) + ' / ' + total;
    }

    // Coalesce the scroll storm into one update per frame by replacing the
    // pending callback rather than gating on a flag: a flag that is cleared
    // inside the callback stays stuck if the frame never comes — which is
    // exactly what a backgrounded tab does — and the dots then stop tracking
    // the strip for the rest of the page's life. sync() reads the live scroll
    // position, so dropping intermediate frames costs nothing.
    var tick = 0;
    track.addEventListener('scroll', function () {
      cancelAnimationFrame(tick);
      tick = requestAnimationFrame(sync);
    });

    var prev = root.querySelector('[data-carousel-prev]');
    var next = root.querySelector('[data-carousel-next]');
    if (prev) prev.addEventListener('click', function () { go(index - 1); });
    if (next) next.addEventListener('click', function () { go(index + 1); });

    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
    });

    // Slides are sized in percentages, so a resize moves the snap points.
    window.addEventListener('resize', function () {
      track.scrollTo({ left: index * track.clientWidth, behavior: 'instant' });
    });

    sync();
  }
})();
