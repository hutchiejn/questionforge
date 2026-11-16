(() => {
  const preview = document.getElementById('demo-display');
  const image = document.getElementById('demo-image');
  const label = document.getElementById('demo-top-label');
  const description = document.getElementById('demo-description');
  const buttons = Array.from(document.querySelectorAll('[data-preview]'));
  if (!preview || !image || !label || !description || buttons.length === 0) return;

  const views = {
    review: {
      src: 'assets/question-review.png',
      alt: 'QuestionForge editable question bank showing question types and counts',
      label: 'QUESTION REVIEWER',
      description: 'Your question bank, before anything goes to print.'
    },
    export: {
      src: 'assets/hero-paper-sample.png',
      alt: 'A sample assessment paper exported by QuestionForge',
      label: 'FORMATTED PAPER',
      description: 'The reviewed questions, laid out as a printable exam.'
    }
  };
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const key = button.dataset.preview;
      const view = views[key];
      if (!view) return;
      preview.dataset.view = key;
      image.src = view.src;
      image.alt = view.alt;
      label.textContent = view.label;
      description.textContent = view.description;
      buttons.forEach(item => {
        const active = item === button;
        item.classList.toggle('active', active);
        item.setAttribute('aria-pressed', String(active));
      });
    });
  });
})();
