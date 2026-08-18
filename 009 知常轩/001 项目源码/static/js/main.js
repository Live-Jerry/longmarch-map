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

/* 破折号渲染加固：把 "——" 包进 .dash-join，强制黑体连续渲染，避免不同设备/字体下断开 */
(function () {
  var SKIP = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|PRE|CODE)$/;
  function wrapDashes(node) {
    if (node.nodeType === 3) {
      var t = node.nodeValue;
      if (t.indexOf('\u2014') === -1) return;
      var frag = document.createDocumentFragment();
      var parts = t.split(/(\u2014+)/);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        if (/^\u2014+$/.test(p)) {
          var span = document.createElement('span');
          span.className = 'dash-join';
          span.textContent = p;
          frag.appendChild(span);
        } else if (p) {
          frag.appendChild(document.createTextNode(p));
        }
      }
      node.parentNode.replaceChild(frag, node);
    } else if (node.nodeType === 1 && !SKIP.test(node.tagName)) {
      var kids = Array.prototype.slice.call(node.childNodes);
      for (var j = 0; j < kids.length; j++) wrapDashes(kids[j]);
    }
  }
  if (document.body) wrapDashes(document.body);
})();
