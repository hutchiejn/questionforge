# QuestionForge Figma website redesign

Reference file: https://www.figma.com/design/FcD2tPVPGVYbkZOgQu3KsS/Untitled?node-id=0-1

Implemented: Figma-inspired Home (frame 1:932), Help Center/FAQ (1:584), and User Guide (1:2). The same visual language is applied to Privacy, Contact, and 404.

- Figma visual tokens: #FAFBF8 canvas, #0B120E ink, #00885A green, #E2E8E3 borders; Space Grotesk headings, Plus Jakarta Sans body, JetBrains Mono microcopy.
- Home includes responsive side-by-side paper/review mockups, source preparation mockup, existing functional review/final paper tab switch, editorial chapters, feature steps, and privacy strip.
- FAQ contains accessible native accordions, category filters, and expand/collapse all. Existing 11 questions were retained.
- Guide retains real v0.8.4 ZIP link and hash, adds a copy-hash action, more legible numbered steps and sticky table of contents.
- Shared desktop/mobile navigation, dark theme, and footer preserved.
- The production ZIP is unchanged, and the SHA-256 fingerprint remains 036d321b10e65f4041581353d51efc2904f4927038144c8b4cdef691a8527b51.
- No editable extension code, development tests, Git metadata or source maps are shipped outside the production ZIP.

## Local preview

Run `python -m http.server 8000` from this directory, then visit `http://localhost:8000/`. There is no build step. On Vercel, set framework preset to **Other** and serve from the repository root.

## Verification

Completed static checks: HTML parsing, local URL existence, CSS parsing, JavaScript syntax and release ZIP SHA-256. A browser pixel-comparison check was unavailable in the execution environment; review desktop/mobile appearance in your browser before deploying.


## Follow-up corrections (November 16, 2026)

- Reorganized the Guide installation download card as a responsive header + download action, separate SHA-256 checksum section, and a full-width note. This prevents horizontal content squeeze and wraps the checksum safely without cutting off the Copy hash button.
- Removed the nested dark, bordered image wrapper from the homepage Review / Final paper demonstration. The review screenshot is shown as a larger viewport-width image instead of a 220px thumbnail; the document preview displays at a considerably larger scale while retaining its full sheet.
- Added the same QuestionForge QF brand mark already used by the site on top of the paper image's unrelated sample insignia. The underlying sample remains demonstration-only, not a generated document or a product feature change.
- Maintained the actual downloadable production package and unchanged SHA-256.

## Theme contrast patch (November 16, 2026)

- Added `assets/accessibility-contrast.css` as the last stylesheet on every page.
- Corrected dark and light button contrast, including navigation CTA, release download, Copy hash, FAQ filters, Review / Final paper tabs, footer links, and GCash download.
- Updated the dark-mode guide and privacy sidebars with readable inactive and selected links, headings and environment notes.
- Updated warning/success callouts, inline code, and the dark-mode contact donation panel so both foreground and background adapt together.
- Added green emphasis to key documented workflow actions in the guide; wording and links are unchanged.
- Kept extension ZIP and SHA-256 checksum unchanged.
