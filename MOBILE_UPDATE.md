# QuestionForge website — Mobile refresh (v1.7)

This version builds on the previous public website (v1.6), including its production-only QuestionForge v0.8.4 ZIP download. The desktop website and existing legal pages are retained.

## Changes
- Accessible mobile navigation with overlay, Escape key support, link-close behavior, scroll lock, and clear menu control.
- Mobile product screenshots are horizontally swipeable using native CSS scroll snapping; desktop overlap remains unchanged.
- Improved type scale, hero CTA spacing, readable feature cards, and compact steps.
- One-line horizontally scrollable section links on help/privacy pages.
- Mobile-friendly install button, checksum wrapping, and installation steps.
- Scrollable guide screenshot strip, accessible GCash support card, and improved footer columns.
- Light/dark theme styles preserved across all pages.
- No new network dependencies, external fonts, frameworks, analytics, or payment handling.

## Deploy to Vercel
Use the **Other** framework preset and the folder containing `index.html` as the output root. No build command is needed. The download inside `downloads/` is the pre-existing production package and is intentionally unchanged.

## Test before release
- Check 320, 360, 390, and 430px mobile widths in Chrome and Safari.
- Open/close the menu, change theme, swipe hero previews and guide images.
- Verify GCash receiving QR against your intended account, and check the public support/contact information.
- Install and smoke-test the included extension independently.
