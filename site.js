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
})();
