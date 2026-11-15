(() => {
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('site-navigation');
  if (toggle && nav) {
    const backdrop = document.querySelector('[data-nav-scrim]');
    const label = toggle.querySelector('.menu-label');
    const closeMenu = (restoreFocus = false) => {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open navigation menu');
      if (label) label.textContent = 'Menu';
      nav.classList.remove('open');
      document.body.classList.remove('mobile-nav-open');
      if (restoreFocus) toggle.focus();
    };
    const openMenu = () => {
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close navigation menu');
      if (label) label.textContent = 'Close';
      nav.classList.add('open');
      document.body.classList.add('mobile-nav-open');
      const firstLink = nav.querySelector('a');
      firstLink?.focus();
    };
    toggle.addEventListener('click', () => {
      nav.classList.contains('open') ? closeMenu(true) : openMenu();
    });
    backdrop?.addEventListener('click', () => closeMenu(true));
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('open')) closeMenu(true);
      if (event.key === 'Tab' && nav.classList.contains('open') && window.innerWidth <= 760) {
        const nodes = Array.from(nav.querySelectorAll('a:not([tabindex="-1"])'));
        const first = nodes[0], last = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 760 && nav.classList.contains('open')) closeMenu();
    });
  }
  // Theme state is shared across all pages. If storage is unavailable, toggle still works for this page.
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    if (themeToggle) {
      themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      themeToggle.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#111512' : '#fafbf8';
  };
  applyTheme(document.documentElement.dataset.theme || 'light');
  themeToggle?.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem('questionforge.website.theme', next); } catch {}
  });
  const tocLinks = document.querySelectorAll('.toc a[href^="#"]');
  tocLinks.forEach(link => link.addEventListener('click', () => {
    tocLinks.forEach(el => el.classList.remove('active'));
    link.classList.add('active');
  }));
})();
