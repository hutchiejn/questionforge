async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const results = [];
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const theme of ['dark', 'light']) {
      for (const name of ['index', 'guide', 'faq']) {
        await page.goto(`http://127.0.0.1:8000/${name}.html`, { waitUntil: 'domcontentloaded' });
        await page.evaluate(theme => localStorage.setItem('questionforge.website.theme', theme), theme);
        await page.reload({ waitUntil: 'domcontentloaded' });
        if (name === 'index') await page.locator('.prepare-screen').scrollIntoViewIfNeeded();
        if (name === 'guide') {
          await page.locator('.guide-screens').scrollIntoViewIfNeeded();
          await page.locator('.guide-screen').first().locator('img:visible').evaluate(image => image.decode());
        }
        const details = await page.evaluate(({ name, theme }) => {
          const assert = (test, message) => { if (!test) throw new Error(message); };
          assert(document.documentElement.dataset.theme === theme, 'Wrong theme');
          assert(document.documentElement.scrollWidth <= innerWidth, 'Page horizontal overflow');
          if (name === 'index') {
            const luminance = color => {
              const channels = color.match(/[\d.]+/g).slice(0, 3).map(Number).map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
              return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722;
            };
            let minimum = Infinity;
            for (const selector of ['.prepare-topline span:last-child', '.prepare-intro strong', '.prepare-upload b']) {
              const element = document.querySelector(selector);
              const foreground = getComputedStyle(element).color;
              let node = element, background = getComputedStyle(node).backgroundColor;
              while (background === 'rgba(0, 0, 0, 0)' && node.parentElement) {
                node = node.parentElement; background = getComputedStyle(node).backgroundColor;
              }
              const a = luminance(foreground), b = luminance(background);
              const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
              assert(ratio >= 4.5, `Low preparation contrast: ${selector} ${ratio}`);
              minimum = Math.min(minimum, ratio);
            }
            return { minimumContrast: Math.round(minimum * 100) / 100 };
          }
          if (name === 'guide') {
            const visible = [...document.querySelectorAll('.guide-screen:first-child img')].filter(img => getComputedStyle(img).display !== 'none');
            assert(visible.length === 1, 'Prompt must show exactly one themed image');
            const image = visible[0];
            assert(image.getAttribute('src') === `assets/prompt-builder${theme === 'dark' ? '-dark' : ''}.png`, 'Wrong themed prompt image');
            assert(image.naturalWidth === 390 && image.naturalHeight === 940, 'New capture missing');
            return { promptImage: image.getAttribute('src') };
          }
          const items = [...document.querySelectorAll('.faq-item')];
          assert(items.length === 14, 'FAQ total incorrect');
          assert(document.querySelector('[data-faq-filter=all]').textContent === 'All Questions (14)', 'FAQ count label incorrect');
          assert(items.map(item => Number(item.querySelector('.faq-item-number').textContent)).every((number, i) => number === i + 1), 'FAQ numbering incorrect');
          assert(!document.body.innerText.includes('eliminate hallucinated outputs'), 'Misleading AI accuracy claim remains');
          document.querySelector('[data-faq-filter="AI Chatbot Workflow"]').click();
          const visible = items.filter(item => !item.hidden);
          assert(visible.length === 6 && visible.every(item => item.dataset.faqCategory === 'AI Chatbot Workflow'), 'FAQ category filtering broken');
          document.querySelector('#faq-expand').click();
          assert(visible.every(item => item.open), 'FAQ expansion broken');
          document.querySelector('#faq-expand').click();
          assert(visible.every(item => !item.open), 'FAQ collapse broken');
          document.querySelector('[data-faq-filter=all]').click();
          assert(items.every(item => !item.hidden), 'All questions filter broken');
          return { totalQuestions: items.length, chatbotQuestions: visible.length };
        }, { name, theme });
        if (name === 'index') await page.locator('.home-chapter-media--plan').screenshot({ path: `output/playwright/prepare-fixed-${theme}-${width}.png` });
        if (name === 'guide') await page.locator('.guide-screens').screenshot({ path: `output/playwright/guide-prompts-${theme}-${width}.png` });
        if (name === 'faq' && width === 1440 && theme === 'dark') await page.screenshot({ path: 'output/playwright/faq-updated-dark.png', fullPage: true });
        results.push({ name, theme, width, ...details });
      }
    }
  }
  if (errors.length) throw new Error(errors.join('\n'));
  return { results, pageErrors: errors };
}
