async (page) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.addInitScript(() => Object.defineProperty(navigator, 'clipboard', {
    configurable: true, value: {writeText: async value => {window.__releaseCopied = value;}}
  }));
  const checked = [];
  for (const port of [8000,8003]) {
    for (const width of [1440,390]) {
      await page.setViewportSize({width,height:1000});
      for (const theme of ['light','dark']) {
        await page.goto(`http://127.0.0.1:${port}/guide.html`,{waitUntil:'domcontentloaded'});
        await page.evaluate(theme => localStorage.setItem('questionforge.website.theme',theme),theme);
        await page.reload({waitUntil:'domcontentloaded'});
        const details = await page.evaluate(async () => {
          const release = await (await fetch('release.json')).json();
          const assert = (test,message) => {if(!test)throw new Error(message);};
          assert(document.documentElement.scrollWidth <= innerWidth,'Release card caused page overflow');
          assert(document.querySelector('[data-release=download]').getAttribute('href') === release.download_url,'Download URL mismatch');
          assert(document.querySelector('[data-release=sha256]').textContent === release.sha256,'Displayed checksum mismatch');
          assert(document.querySelector('[data-release=copy-hash]').dataset.copyHash === release.sha256,'Copy checksum mismatch');
          assert([...document.querySelectorAll('[data-release=version]')].every(node=>node.textContent === 'v'+release.version),'Version label mismatch');
          assert(getComputedStyle(document.querySelector('.footer-bottom [data-release=version]')).display === 'inline','Footer version should stay inline');
          return {version:release.version,url:release.download_url,sha256:release.sha256};
        });
        await page.getByRole('button',{name:'Copy SHA-256 checksum'}).click();
        if(await page.evaluate(()=>window.__releaseCopied) !== details.sha256) throw new Error('Copy handler used stale hash');
        if(await page.getByRole('button',{name:'Copy SHA-256 checksum'}).textContent() !== 'Copied!') throw new Error('Missing copy feedback');
        if(port === 8003 && theme === 'dark') await page.locator('.download-box').screenshot({path:`output/playwright/release-automated-${width}.png`});
        checked.push({port,width,theme,...details});
      }
    }
  }
  for (const name of ['index','faq','privacy','contact','404']) {
    await page.goto(`http://127.0.0.1:8003/${name}.html`,{waitUntil:'domcontentloaded'});
    const badge = await page.locator('.release-badge').textContent();
    if(badge !== 'v0.8.5 Beta') throw new Error('Stale badge on '+name);
  }
  if(errors.length) throw new Error(errors.join('\n'));
  return {guideCases:checked.length,otherPages:5,copyHandler:'passed',pageErrors:errors};
}
