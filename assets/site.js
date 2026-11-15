(() => {
  const toggle = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('site-navigation');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      toggle.textContent = expanded ? 'Menu ☰' : 'Close ×';
      nav.classList.toggle('open', !expanded);
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = 'Menu ☰';
        toggle.focus();
      }
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
