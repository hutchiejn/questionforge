# QuestionForge website v1.3 — Brand cleanup and theme support

- Fixed the legacy star icon and broken image/wordmark inside two product screenshots using the approved QF monogram.
- Removed the two outdated screenshot versions from the distributable assets to avoid reintroducing the retired branding.
- Added dark/light switch to all six pages, persistent in browser localStorage, with system preference fallback and no external dependencies.
- Added cohesive inline SVG feature icons instead of miscellaneous text glyphs.
- Improved hero and content sections, image presentation, page contrast, navigation, focus states, and mobile spacing.
- Dark mode changes page colors; the app image swaps to its dark-mode screenshot where available.
- The app itself is unchanged, including the extension download archive.

## Publish

Copy the contents of this folder to your static website host (e.g. GitHub Pages). No build step is required.

## Test

Open `index.html` with a simple local HTTP server and toggle the moon/sun button. Open `guide.html`, `faq.html`, `privacy.html`, and `contact.html` to confirm the preference carries across pages.


## v1.4 follow-up fixes
- Removed framed outer containers around the homepage screenshots.
- Switched the header brand to a dark-mode-specific logo card.
- Fixed the download button contrast and width in dark mode.
- Added footer and contact-page support buttons for Buy Me a Coffee and GCash.
