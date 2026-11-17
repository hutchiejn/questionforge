async (page) => {
  const captures = [];
  for (const theme of ['dark', 'light']) {
    if (await page.locator('html').getAttribute('data-theme') !== theme) {
      await page.getByRole('button', { name: `Switch to ${theme} mode` }).click();
    }
    await page.locator('.prompt-view').waitFor();
    await page.evaluate(() => {
      const walker = document.createTreeWalker(document.querySelector('#app'), NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const text = walker.currentNode;
        text.nodeValue = text.nodeValue
          .replace('Tell ChatGPT what to assess.', 'Tell your AI chatbot what to assess.')
          .replace('or continue attaching documents in ChatGPT.', 'or attach documents in your chosen AI chatbot.')
          .replace('Attach in ChatGPT', 'Attach in AI chatbot')
          .replaceAll('ChatGPT', 'your AI chatbot');
      }
      document.querySelector('.scroll-area').scrollTop = 0;
      if (document.querySelector('#app').innerText.includes('ChatGPT')) throw new Error('Provider-specific preview text remains');
    });
    await page.locator('.app-header img').first().evaluate(img => img.decode());
    const path = `output/playwright/prompt-builder${theme === 'dark' ? '-dark' : ''}.png`;
    await page.screenshot({ path });
    captures.push({ theme, path, width: 390, height: 940 });
  }
  return captures;
}
