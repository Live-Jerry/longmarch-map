/* 知常轩主站 JS V1.0 */
(function () {
  'use strict';

  // 移动端导航切换
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // 图片懒加载（V2.2 移动端要求）
  if ('IntersectionObserver' in window) {
    var imgs = document.querySelectorAll('img[data-src]');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          img.src = img.getAttribute('data-src');
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      });
    });
    imgs.forEach(function (img) { observer.observe(img); });
  }
})();
