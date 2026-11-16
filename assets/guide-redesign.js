(() => {
  const copy = document.querySelector('[data-copy-hash]');
  if (copy) copy.addEventListener('click', async () => {
    const checksum = copy.dataset.copyHash;
    let copied = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(checksum);
        copied = true;
      } else {
        const temp = document.createElement('textarea');
        temp.value = checksum;
        temp.setAttribute('readonly', '');
        temp.style.position = 'fixed';
        temp.style.opacity = '0';
        document.body.appendChild(temp);
        temp.select();
        copied = document.execCommand('copy');
        temp.remove();
      }
    } catch { copied = false; }
    copy.textContent = copied ? 'Copied!' : 'Select hash above';
    if (!copied) document.getElementById('release-sha-value')?.focus?.();
    setTimeout(() => { copy.textContent = 'Copy hash'; }, 2500);
  });
  const headings = [...document.querySelectorAll('.guide-article > section[id]')];
  const anchors = [...document.querySelectorAll('.guide-toc > a[href^="#"]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        anchors.forEach(a => a.classList.toggle('active', a.hash === '#' + entry.target.id));
      });
    }, {rootMargin:'-95px 0px -60% 0px'});
    headings.forEach(section => observer.observe(section));
  }
})();
