async (page) => {
  await page.setViewportSize({width:1440,height:1000});
  await page.evaluate(() => localStorage.setItem('questionforge.website.theme', 'dark'));
  await page.reload({waitUntil:'domcontentloaded'});
  const colors = await page.evaluate(() => {
    return ['.faq-item-number', '.faq-arch-card>.section-number'].map(selector => {
      const color = getComputedStyle(document.querySelector(selector)).color;
      if (color !== 'rgb(166, 243, 201)') throw new Error(`FAQ label is too faint: ${selector} ${color}`);
      return {selector,color};
    });
  });
  await page.screenshot({path:'output/playwright/faq-updated-dark.png',fullPage:true});
  return {faqContrast:'passed',colors};
}
