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

  // ---- gallery carousel -------------------------------------------------
  // The slides are a native scroll-snapping strip (see site.css). Nothing here
  // moves them; it only scrolls the strip and keeps the dots and counter in
  // step with wherever the strip actually is, so dragging, arrow keys and the
  // buttons can't disagree about which photo is showing.
  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var track = root.querySelector('.carousel-track');
    var slides = root.querySelectorAll('.carousel-slide');
    var dotsWrap = root.querySelector('.carousel-dots');
    var count = root.querySelector('.carousel-count');
    if (!track || slides.length < 2) return;

    var index = 0;
    var dots = [];

    function go(i) {
      var n = (i % slides.length + slides.length) % slides.length;
      // Going off either end wraps. Animating that would rewind through every
      // slide in between, so wraps jump and only ordinary steps glide.
      var wrapped = i < 0 || i >= slides.length;
      track.scrollTo({
        left: n * track.clientWidth,
        behavior: (reduced || wrapped) ? 'auto' : 'smooth'
      });
    }

    if (dotsWrap) {
      slides.forEach(function (slide, i) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'carousel-dot';
        dot.setAttribute('aria-label', 'Photo ' + (i + 1) + ' of ' + slides.length);
        dot.addEventListener('click', function () { go(i); });
        dotsWrap.appendChild(dot);
        dots.push(dot);
      });
    }

    function sync() {
      var w = track.clientWidth;
      if (!w) return;
      index = Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / w)));
      dots.forEach(function (dot, i) {
        dot.setAttribute('aria-current', i === index ? 'true' : 'false');
      });
      if (count) count.textContent = (index + 1) + ' / ' + slides.length;
    }

    var pending = false;
    track.addEventListener('scroll', function () {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; sync(); });
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
      track.scrollTo({ left: index * track.clientWidth, behavior: 'auto' });
    });

    sync();
  });
})();
