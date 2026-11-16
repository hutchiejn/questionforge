# QuestionForge website v1.9 — Homepage redesign

The homepage has been redesigned with an original editorial visual language informed by the **layout principles** of ponytail.dev: direct oversized typography, restrained color, numbered sections, and product demonstrations. No layouts, illustrations, copy, or code have been copied from the reference site.

## Updated files
- `index.html`: new homepage narrative and interactive review/print preview
- `assets/home.css`: scoped homepage styles for light/dark and responsive widths
- `assets/home.js`: progressive-enhancement preview toggle; no external services

## Kept unchanged
- Legal pages, FAQ, contact, guide and 404 page
- QF monogram, production ZIP download, GCash assets and privacy disclosures
- No backend, analytics or third-party JS (v2.1 uses Google Fonts for typography)

## Deploy
Upload the entire `questionforge-website` folder contents to your Vercel project root. If upgrading a previously deployed site, a three-file patch (`index.html`, `assets/home.css`, and `assets/home.js`) is sufficient.

## Important
The hero uses two **separate product examples**, not a before/after of the same question set. The interactive preview uses real existing QuestionForge screenshots. Test on your hosted Vercel URL after deployment.
