async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const checked = [];
  for (const width of [1440, 390]) {
    await page.setViewportSize({width,height:1000});
    for (const theme of ['light','dark']) {
      for (const name of ['index','faq','guide','privacy','contact','404']) {
        await page.goto(`http://127.0.0.1:8000/${name}.html`,{waitUntil:'domcontentloaded'});
        await page.evaluate(theme => localStorage.setItem('questionforge.website.theme',theme),theme);
        await page.reload({waitUntil:'domcontentloaded'});
        const result = await page.evaluate(() => ({
          overflow:document.documentElement.scrollWidth > innerWidth,
          themeButtonRadius:getComputedStyle(document.querySelector('.theme-switch')).borderRadius,
          panelRadii:[...document.querySelectorAll('.faq-item,.toc,.contact-card,.prepare-window')].slice(0,3).map(node=>getComputedStyle(node).borderRadius)
        }));
        if(result.overflow) throw new Error(`Horizontal overflow: ${name} ${theme} ${width}`);
        if(name==='index'||name==='faq') await page.screenshot({path:`output/playwright/rounded-${name}-${theme}-${width}.png`});
        checked.push({page:name,theme,width,...result});
      }
    }
  }
  if(errors.length) throw new Error(errors.join('\n'));
  return {pagesChecked:checked.length,pageErrors:errors,samples:checked.slice(0,6)};
}
