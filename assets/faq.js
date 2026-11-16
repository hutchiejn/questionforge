(() => {
  const items = [...document.querySelectorAll('.faq-item')];
  const filters = [...document.querySelectorAll('[data-faq-filter]')];
  const expand = document.getElementById('faq-expand');
  filters.forEach(button => button.addEventListener('click', () => {
    const category = button.dataset.faqFilter;
    items.forEach(item => { item.hidden = category !== 'all' && item.dataset.faqCategory !== category; });
    filters.forEach(tab => { const selected = tab === button; tab.classList.toggle('selected', selected); tab.setAttribute('aria-pressed', String(selected)); });
    document.querySelector('.faq-empty').hidden = items.some(item => !item.hidden);
    if (expand) expand.textContent = 'Expand all';
  }));
  expand?.addEventListener('click', () => {
    const visible = items.filter(item => !item.hidden);
    const shouldExpand = visible.some(item => !item.open);
    visible.forEach(item => item.open = shouldExpand);
    expand.textContent = shouldExpand ? 'Collapse all' : 'Expand all';
  });
  items.forEach(item => item.addEventListener('toggle', () => {
    if (!expand) return;
    const visible = items.filter(x => !x.hidden);
    expand.textContent = visible.length && visible.every(x => x.open) ? 'Collapse all' : 'Expand all';
  }));
})();
