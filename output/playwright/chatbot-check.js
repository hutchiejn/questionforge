async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const results = [];
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const theme of ['light', 'dark']) {
      for (const name of ['index', 'guide', 'faq']) {
        await page.goto(`http://127.0.0.1:8000/${name}.html`, { waitUntil: 'domcontentloaded' });
        await page.evaluate(theme => localStorage.setItem('questionforge.website.theme', theme), theme);
        await page.reload({ waitUntil: 'domcontentloaded' });
        const details = await page.evaluate(({ name, theme }) => {
          const assert = (test, message) => { if (!test) throw new Error(message); };
          const text = document.body.innerText;
          assert(document.documentElement.dataset.theme === theme, 'Wrong theme');
          assert(document.documentElement.scrollWidth <= innerWidth, 'Page horizontal overflow');
          assert(!text.includes('OpenAI'), 'Provider-specific affiliation remains');
          if (name === 'guide') {
            assert(text.split('ChatGPT').length === 2 && text.includes('Attach in ChatGPT'), 'Guide must preserve only the actual UI label');
            assert(text.includes('required JSON format'), 'Chatbot output requirements missing');
          } else assert(!text.includes('ChatGPT'), 'Provider-specific copy remains');
          if (name === 'index') assert(document.querySelector('.home-deck').textContent.includes('your AI chatbot'), 'Hero not updated');
          if (name === 'faq') {
            const button = document.querySelector('[data-faq-filter="AI Chatbot Workflow"]');
            assert(button, 'Renamed FAQ filter missing');
            button.click();
            const visible = [...document.querySelectorAll('.faq-item')].filter(item => !item.hidden);
            assert(visible.length === 2 && visible.every(item => item.dataset.faqCategory === 'AI Chatbot Workflow'), 'FAQ filter broken');
            document.querySelector('#faq-expand').click();
            assert(visible.every(item => item.open), 'Expand all broken');
            document.querySelector('[data-faq-filter="all"]').click();
            assert([...document.querySelectorAll('.faq-item')].every(item => !item.hidden), 'All questions filter broken');
          }
          return { page: name, theme, width: innerWidth };
        }, { name, theme });
        if (name === 'index') await page.screenshot({ path: `output/playwright/chatbot-home-${theme}-${width}.png` });
        results.push(details);
      }
    }
  }
  if (errors.length) throw new Error(errors.join('\n'));
  return { checked: results.length, faqFiltering: 'passed', pageErrors: errors };
}
