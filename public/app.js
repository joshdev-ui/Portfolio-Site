(() => {
  'use strict';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let lenis;
  function configureMotion() {
    if (lenis) { lenis.destroy(); lenis = undefined; }
    if (!reducedMotion.matches && typeof window.Lenis === 'function') {
      lenis = new Lenis({ autoRaf: true, duration: 1.35, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothWheel: true, syncTouch: false, wheelMultiplier: 0.9 });
      document.documentElement.dataset.scrollEngine = 'lenis';
    } else document.documentElement.dataset.scrollEngine = 'native';
    document.documentElement.classList.toggle('motion-enabled', !reducedMotion.matches);
  }
  configureMotion();
  reducedMotion.addEventListener('change', configureMotion);

  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
    }), { threshold: 0.08, rootMargin: '0px 0px -20px 0px' });
    reveals.forEach(el => observer.observe(el));
  } else reveals.forEach(el => el.classList.add('is-visible'));

  const menuButton = document.querySelector('.menu-toggle');
  const mobileNav = document.querySelector('.mobile-nav');
  function closeMenu() { mobileNav.hidden = true; menuButton.setAttribute('aria-expanded', 'false'); menuButton.setAttribute('aria-label', 'Open navigation'); }
  menuButton.addEventListener('click', () => {
    const opened = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(opened));
    menuButton.setAttribute('aria-label', opened ? 'Close navigation' : 'Open navigation');
    mobileNav.hidden = !opened;
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !mobileNav.hidden) { closeMenu(); menuButton.focus(); } });
  document.addEventListener('click', event => { if (!mobileNav.hidden && !event.target.closest('.site-header')) closeMenu(); });
  window.matchMedia('(min-width: 801px)').addEventListener('change', event => { if (event.matches) closeMenu(); });

  document.querySelectorAll('a[href^="#"]').forEach(anchor => anchor.addEventListener('click', event => {
    const href = anchor.getAttribute('href');
    const destination = document.querySelector(href);
    if (!destination) return;
    event.preventDefault(); closeMenu();
    const focusDestination = () => { if (!destination.hasAttribute('tabindex')) destination.setAttribute('tabindex', '-1'); destination.focus({ preventScroll: true }); };
    if (lenis) lenis.scrollTo(destination, { offset: 0, onComplete: focusDestination });
    else { destination.scrollIntoView({ behavior: 'auto', block: 'start' }); focusDestination(); }
    if (location.hash !== href) history.pushState(null, '', href);
  }));

  const progress = document.querySelector('.scroll-progress');
  let scrollFramePending = false;
  const updateProgress = () => {
    const height = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${height > 0 ? Math.min(1, window.scrollY / height) : 0})`;
    scrollFramePending = false;
  };
  window.addEventListener('scroll', () => { if (!scrollFramePending) { scrollFramePending = true; requestAnimationFrame(updateProgress); } }, { passive: true });
  window.addEventListener('resize', updateProgress); updateProgress();

  const cursor = document.querySelector('.cursor');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  let cursorFrame;
  let pointerX = -100, pointerY = -100;
  window.addEventListener('pointermove', event => {
    if (!finePointer.matches || reducedMotion.matches || event.pointerType === 'touch') return;
    pointerX = event.clientX; pointerY = event.clientY;
    cursor.classList.add('visible');
    cursor.classList.toggle('on-link', Boolean(event.target.closest('a, button, input, textarea')));
    if (!cursorFrame) cursorFrame = requestAnimationFrame(() => {
      cursor.style.transform = `translate(${pointerX}px, ${pointerY}px) translate(-50%, -50%)`;
      cursorFrame = null;
    });
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', () => cursor.classList.remove('visible'));
  window.addEventListener('blur', () => cursor.classList.remove('visible'));

  const slides = [
    { text: 'I learn by building. Developing my own web and mobile applications gives me hands-on practice connecting interfaces, databases, and real-world workflows.', label: 'Build with purpose', detail: ' / Personal development' },
    { text: 'A useful application connects the whole experience. My hands-on work includes database integration, media uploads, offline storage, and real-time messaging.', label: 'Connect the pieces', detail: ' / Web & mobile' },
    { text: 'My next step is an internship or entry-level opportunity where I can contribute, learn from a team, and grow toward full-stack development with an interest in AI.', label: 'Keep growing', detail: ' / The next chapter' }
  ];
  let activeSlide = 0;
  const dots = [...document.querySelectorAll('[data-slide]')];
  function showSlide(index) {
    activeSlide = (index + slides.length) % slides.length;
    document.querySelector('#approach-text').textContent = slides[activeSlide].text;
    document.querySelector('#approach-label').textContent = slides[activeSlide].label;
    document.querySelector('#approach-detail').textContent = slides[activeSlide].detail;
    dots.forEach((dot, i) => { dot.classList.toggle('active', i === activeSlide); dot.setAttribute('aria-pressed', String(i === activeSlide)); });
  }
  document.querySelector('.previous').addEventListener('click', () => showSlide(activeSlide - 1));
  document.querySelector('.next').addEventListener('click', () => showSlide(activeSlide + 1));
  dots.forEach(dot => dot.addEventListener('click', () => showSlide(Number(dot.dataset.slide))));
  document.querySelector('.approach-slider').addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); showSlide(activeSlide - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); showSlide(activeSlide + 1); }
  });

  const form = document.querySelector('#contact-form');
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const name = String(data.get('name')).trim();
    const message = String(data.get('message')).trim();
    const status = document.querySelector('#form-status');
    if (!name || !message) { status.textContent = 'Please add your name and a message before continuing.'; return; }
    const email = String(data.get('email')).trim();
    const phone = String(data.get('phone')).trim();
    const body = `Hi Joshua,\n\n${message}\n\nFrom: ${name}\nEmail: ${email}${phone ? `\nPhone: ${phone}` : ''}`;
    const target = `mailto:joshuasarno.edu.ph@gmail.com?subject=${encodeURIComponent(`Portfolio inquiry from ${name}`)}&body=${encodeURIComponent(body)}`;
    const link = document.createElement('a');
    link.href = target; link.hidden = true; document.body.appendChild(link); link.click(); link.remove();
    status.textContent = 'Your email draft is ready to open. Send it from your email app. If nothing opens, email joshuasarno.edu.ph@gmail.com directly. Your message remains here.';
  });
  document.querySelector('#year').textContent = new Date().getFullYear();
})();
