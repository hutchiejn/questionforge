# QuestionForge public website links (extension v0.8.4)

This website contains `privacy.html` and `contact.html`. Until you actually publish them and verify their **HTTPS** URLs, the extension safely opens its bundled offline copies. **Do not use questionforge.app or questionforge.ai** merely because those sites share a name: they describe other products.

## After publishing the website

1. Open `https://YOUR-ACTUAL-SITE/privacy.html` and `https://YOUR-ACTUAL-SITE/contact.html` and verify both load and show your QuestionForge pages.
2. Run the private utility `configure_official_site.py` against the production extension ZIP, passing the real site root (including a GitHub Pages project prefix, if any).
3. The utility adds `homepage_url` to the production `manifest.json`; the extension then opens the published legal pages from **About** and **Privacy & Security**. It does not add new Chrome permissions or network calls.
4. Run the utility with `--website-dir` to update the website download and its printed SHA-256. Publish the updated site and ZIP together.
5. Open `chrome://extensions`, reload the unpacked extension, and test both links.

Do not replace the website download with the private source or the build tooling.
