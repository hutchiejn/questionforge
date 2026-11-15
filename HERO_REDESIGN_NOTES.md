# QuestionForge homepage hero refresh

This release replaces only the homepage hero and leaves the FAQ, guide, privacy, contact, installation, and download links unchanged.

## Changed
- Replaced vague headline with specific description of the outcome: From questions to exam papers.
- Removed neon-on-dark styling, graph-paper grid, fake browser window, three marketing claims, and decorative badges.
- Used a quiet warm-white canvas with charcoal typography and restrained emerald accent.
- Replaced the older hero screenshot (which displayed a broken extension logo) with a genuine question-review crop and an actual rendered sample Word assessment.
- Kept product claims precise: documents are reviewed locally; ChatGPT generates questions in a separate workflow; exporting works through Word and print-to-PDF.
- Kept primary CTA pointed at manual installation instructions, not an unlisted Chrome Web Store page.
- Created a responsive visual without depending on JavaScript, custom fonts, or network requests.

## Files updated
- index.html
- assets/site.css
- assets/hero-review-detail.png (cropped from existing extension capture)
- assets/hero-paper-sample.png (sample output from QuestionForge)

## Deployment
Upload the site folder as before. No build step or new dependency.
