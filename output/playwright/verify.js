async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const results = [];
  for (const name of ['index', 'guide', 'faq', 'privacy', 'contact', '404']) {
    await page.goto(`http://127.0.0.1:8000/${name}.html`);
    await page.evaluate(() => {
      if (!document.body.classList.contains('qforge-site') || document.body.classList.contains('figma-site')) throw new Error('Wrong body class');
      const sheet = [...document.styleSheets].find(sheet => sheet.href && sheet.href.endsWith('/assets/qforge.css'));
      if (!sheet || !sheet.cssRules.length) throw new Error('Renamed stylesheet failed to load');
      if (document.querySelector('link[href*=figma-redesign]')) throw new Error('Old stylesheet reference');
    });
    results.push({ page: name, renamedStylesheet: 'loaded', bodyClass: 'qforge-site' });
  }

  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const theme of ['dark', 'light']) {
      for (const name of ['guide', 'index']) {
        await page.goto(`http://127.0.0.1:8000/${name}.html`);
        await page.evaluate(theme => localStorage.setItem('questionforge.website.theme', theme), theme);
        await page.reload();
        const selector = name === 'guide' ? '.guide-screens' : '.export-preview-frame';
        await page.locator(selector).scrollIntoViewIfNeeded();
        for (const img of await page.locator(selector).locator('img').all()) {
          await img.scrollIntoViewIfNeeded();
          await img.evaluate(image => image.decode());
        }
        if (name === 'guide') await page.locator(selector).evaluate(gallery => gallery.scrollLeft = 0);
        const details = await page.evaluate(({ name, theme }) => {
          const assert = (test, message) => { if (!test) throw new Error(message); };
          assert(document.documentElement.dataset.theme === theme, 'Theme preference failed');
          assert(document.documentElement.scrollWidth <= innerWidth, 'Page overflows viewport');
          if (name === 'guide') {
            const cards = [...document.querySelectorAll('.guide-screen')];
            assert(cards.length === 3, 'Missing guide cards');
            cards.forEach(card => {
              const caption = card.querySelector('figcaption');
              const style = getComputedStyle(caption);
              assert(parseFloat(style.paddingLeft) >= 16 && parseFloat(style.paddingRight) >= 16, 'Caption spacing missing');
              assert(card.querySelector('img').naturalWidth > 0, 'Screenshot missing');
              assert(getComputedStyle(card).backgroundColor === (theme === 'dark' ? 'rgb(25, 35, 29)' : 'rgb(240, 238, 230)'), 'Wrong card background');
            });
            return { cards: cards.length, captionPadding: getComputedStyle(cards[0].querySelector('figcaption')).padding };
          }
          const sheet = document.querySelector('.export-sheet');
          for (const child of sheet.querySelectorAll('strong, b, p')) {
            assert(getComputedStyle(child).color === 'rgb(11, 18, 14)', 'Printed text has wrong color');
          }
          assert(getComputedStyle(sheet).backgroundColor === 'rgb(255, 255, 255)', 'Paper background changed');
          return { paperText: getComputedStyle(sheet).color };
        }, { name, theme });
        await page.locator(selector).screenshot({ path: `output/playwright/${name}-${theme}-${width}.png` });
        results.push({ width, theme, page: name, ...details });
      }
    }
  }
  if (errors.length) throw new Error(errors.join('\n'));
  return { results, pageErrors: errors };
}

