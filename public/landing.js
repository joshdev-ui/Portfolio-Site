(() => {
  'use strict';

  // Run before the body paints; content stays visible if this script is unavailable.
  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const navigation = performance.getEntriesByType('navigation')[0];
  if (reducedMotion.matches || document.hidden || navigation?.type === 'back_forward' ||
      (location.hash && location.hash !== '#home')) return;

  let finished = false;
  let endTimer;
  let frame;
  root.dataset.landing = 'pending';
  const safetyTimer = setTimeout(finish, 3200);

  function finish() {
    if (finished) return;
    finished = true;
    clearTimeout(safetyTimer);
    clearTimeout(endTimer);
    cancelAnimationFrame(frame);
    root.dataset.landing = 'complete';
    window.removeEventListener('scroll', onScroll);
    window.removeEventListener('wheel', finish);
    window.removeEventListener('touchstart', finish);
    document.removeEventListener('pointerdown', finish);
    document.removeEventListener('keydown', finish);
    document.removeEventListener('focusin', finish);
    document.removeEventListener('visibilitychange', onVisibility);
    reducedMotion.removeEventListener('change', onPreference);
    document.dispatchEvent(new Event('portfolio:landing-complete'));
  }

  function onScroll() { if (window.scrollY > 24) finish(); }
  function onVisibility() { if (document.hidden) finish(); }
  function onPreference() { if (reducedMotion.matches) finish(); }

  // The entrance never holds up navigation, scrolling, or keyboard access.
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('wheel', finish, { passive: true });
  window.addEventListener('touchstart', finish, { passive: true });
  document.addEventListener('pointerdown', finish, { passive: true });
  document.addEventListener('keydown', finish);
  document.addEventListener('focusin', finish);
  document.addEventListener('visibilitychange', onVisibility);
  reducedMotion.addEventListener('change', onPreference);
  window.addEventListener('pageshow', event => { if (event.persisted) finish(); });

  async function start() {
    const photo = document.querySelector('.portrait-animation');
    // Briefly allow the local font and portrait to settle, with a bounded wait.
    let readyTimer;
    await Promise.race([
      Promise.allSettled([document.fonts?.ready, photo?.decode?.()]),
      new Promise(resolve => { readyTimer = setTimeout(resolve, 450); })
    ]);
    clearTimeout(readyTimer);
    if (finished) return;
    if (window.scrollY > 24 || reducedMotion.matches || document.hidden) {
      finish();
      return;
    }
    frame = requestAnimationFrame(() => {
      root.dataset.landing = 'playing';
      endTimer = setTimeout(finish, 1600);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else start();
})();
