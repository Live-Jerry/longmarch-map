/* 知常轩主站 JS V1.0 */
(function () {
  'use strict';

  // 移动端导航切换（右侧抽屉：滑入+遮罩，点遮罩/菜单项/Esc 收起，打开时锁定背景滚动）
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  var overlay = document.querySelector('.nav-overlay');

  function setNav(open) {
    if (!toggle || !nav) return;
    nav.classList.toggle('open', open);
    document.body.classList.toggle('nav-open', open);
    if (overlay) overlay.classList.toggle('show', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      setNav(!nav.classList.contains('open'));
    });
    if (overlay) {
      overlay.addEventListener('click', function () { setNav(false); });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setNav(false);
    });
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setNav(false); });
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
