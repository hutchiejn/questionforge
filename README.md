
> **Production security release (November 2026):** Vercel serves only `public/`, with a restrictive Content Security Policy, external integrity monitor support, and protected GCash image checks. See [SECURITY_DEPLOYMENT.md](SECURITY_DEPLOYMENT.md) before deploying. The `public/` directory contains the entire public website; the `tools/` directory and release integrity manifest are not deployed.

> **Website redesign — Figma reference:** Home, FAQ and User Guide have been redesigned using the provided Figma frames. Privacy, Contact and 404 share the new design system. This website distribution contains no editable extension source or Git history.

<div align="center">
  <img src="public/assets/qf-mark-light.svg" alt="QuestionForge QF logo" width="76" height="76" />

  # QuestionForge

  **Good questions deserve a well-made paper.**

  A free, local-first Chrome extension for preparing curriculum-based assessments, reviewing questions, and exporting polished Word and PDF papers.

  [Product overview](public/index.html) · [Getting started](public/guide.html) · [FAQ](public/faq.html) · [Privacy policy](public/privacy.html) · [Contact & support](public/contact.html)
</div>

---

## About the project

**QuestionForge** helps teachers turn AI-generated questions into usable assessments without handing over control of the process. Prepare a coverage plan from a lesson plan, Budget of Work (BOW), Table of Specifications (TOS), or curriculum guide; check the generated questions and answers; then format the finished paper for students or teachers.

QuestionForge **does not generate questions using its own AI model**. It creates structured prompts for use with an AI chatbot that can return the required JSON format, and you choose what source material to share with that service.

**Current status:** developer preview. This repository contains the **public information website** and its **minified production extension download**. It is **not** the editable extension development repository or a Chrome Web Store listing.

## A look at QuestionForge

| Review questions | Format an assessment |
| :---: | :---: |
| ![QuestionForge question review interface](public/assets/hero-review-detail.png) | ![Example formatted assessment](public/assets/hero-paper-sample.png) |

*Screenshots demonstrate the interface and an example paper, not a live interactive demo.*

## What it can do

- **Work from teaching materials.** Import supported DOCX, XLSX, TXT, CSV, and text-based PDF documents; review extracted text and structured tables before approval.
- **Plan before generating.** Create a coverage-planning prompt, review the proposed allocation, and then prepare the exam-generation prompt.
- **Import structured questions.** Prefer JSON for dependable question numbering, types, options, answers, and explanations.
- **Review and correct.** Edit question content, answer choices, points, question types, and answer keys before exporting.
- **Format for the classroom.** Add school details and a logo; choose fonts, paper size, margins, headers, footers, and one- or two-column question layouts.
- **Export documents.** Generate editable Word (`.docx`) documents or use Chrome's Print → Save as PDF.
- **Keep control of your data.** Processing is local to the extension; draft saving is optional. Sending source content to an AI chatbot requires an explicit copy-and-paste action.

### Supported assessment types

Multiple choice · Identification · Enumeration · Essay · True or False

### Important limitations

- Scanned PDFs **do not have automatic OCR** in the current release. Complex PDF layouts and tables may extract incorrectly.
- Source extraction and AI-generated questions **must be checked by a teacher**; neither is guaranteed to be accurate.
- Long teaching documents can exceed external AI context limits, even when split into numbered source packets.
- Saved drafts are **not encrypted by QuestionForge**. Use its no-save setting for sensitive materials.
- QuestionForge does not process GCash payments or verify whether a donation was made.

## How the workflow works

1. **Prepare** — Import or paste relevant teaching material and verify the extracted content.
2. **Plan** — Copy the coverage-planning prompt into your chosen AI chatbot and check its proposed question allocation.
3. **Generate** — After approving the plan, request questions in QuestionForge-compatible structured JSON.
4. **Review** — Import the JSON, inspect question counts and answer keys, and make corrections.
5. **Export** — Select your document layout and generate a Word file or print to PDF.

See the [step-by-step user guide](public/guide.html) for the full process and troubleshooting instructions.

## Install the Chrome extension

QuestionForge is currently provided as a **developer-preview production package**, not an official Chrome Web Store installation.

1. Download the current production ZIP from [Getting started](public/guide.html#install).
2. Extract it locally.
3. Open `chrome://extensions` in Chrome.
4. Turn on **Developer mode** and choose **Load unpacked**.
5. Select the extracted extension folder containing `manifest.json`.
6. Open QuestionForge from the browser toolbar or side panel.

For the published archive's SHA-256 fingerprint and installation notes, see [Getting started](public/guide.html#install). Only install unpacked extensions from sources you trust.

## Website technology

This website is intentionally simple:

| Layer | Technology |
| --- | --- |
| Markup | HTML5 |
| Styling | CSS3 with responsive light and dark themes |
| Interactions | Vanilla JavaScript |
| Hosting | Static hosting, including Vercel |
| Runtime services | No application server, database, or account system |

There is **no npm install** for the website. Vercel runs a standard-library Python build to validate GitHub release metadata and render the current download details. There is no third-party analytics SDK or advertising SDK. The website loads Space Grotesk, Plus Jakarta Sans, and JetBrains Mono from Google Fonts, with system-font fallbacks if unavailable. The site does remember your light/dark theme preference in browser local storage. The hosting provider may maintain its own technical access logs.

### Repository structure

```text
questionforge-website/
├── public/                   # ONLY this directory is published
│   ├── index.html            # Product landing page
│   ├── guide.html            # Installation and user guide
│   ├── faq.html              # Frequently asked questions
│   ├── privacy.html          # Public privacy policy
│   ├── contact.html          # Support and official GCash QR
│   ├── 404.html
│   ├── assets/               # CSS, JS, branding, GCash images
│   ├── release.json           # Release metadata and verified initial fallback
│   └── downloads/
│       └── QuestionForge-v0.8.4-production.zip
├── tools/                    # Audit scripts, NOT published
├── .github/workflows/        # Optional CI security gate
├── release-manifest.json     # Baseline for independent monitoring
├── vercel.json               # CSP and outputDirectory settings
├── SECURITY_DEPLOYMENT.md    # Production hardening checklist
└── README.md
```

## Develop and preview the website locally

You only need Python and a browser to preview the static pages (this local server does **not** simulate Vercel's production security headers):

```bash
cd questionforge-website/public
python -m http.server 8000
```

Visit **http://localhost:8000** and refresh after edits. No npm install is required for local preview; the checked-in pages include the verified fallback release. The extension production ZIP is a separate, already-built download; editing the website does not rebuild it.

To audit the files from the repository root:

```bash
python tools/security_check.py
```

## Release downloads

Publish the prepared production ZIP in `xf00889/questionforge-ext`. The release workflow triggers a Vercel rebuild; the website validates the package and updates its version, pinned GitHub link, file size, and checksum together. No new ZIP needs to be committed to this website. The existing local ZIP remains the fallback until the first release is published.

Follow [the one-time deploy-hook setup and release steps](docs/RELEASES.md). This does not rebuild the extension source.

## Deploy to Vercel

1. Connect the website repository in [Vercel](https://vercel.com/new). **Keep the Vercel Root Directory at the repository root**, where `vercel.json` lives (not inside `public/`).
2. Choose **Framework Preset: Other**. The included `vercel.json` configures **`outputDirectory: "public"`**. Confirm the Vercel dashboard has no conflicting Build & Output Settings override.
3. Keep the included Python build command from `vercel.json`. It validates the current GitHub release, renders the download details, and runs the static audit. Deploy to a preview URL, then validate CSP headers and the donation QR image.
4. Set up GitHub repository variables for the authorized GCash image checksums and protect the production branch before merging. Full steps: [SECURITY_DEPLOYMENT.md](SECURITY_DEPLOYMENT.md).
5. Only promote the release after inspecting the preview and verifying that `privacy.html`, `contact.html`, `guide.html` and the download work over HTTPS.

> The production website URL is not specified here. Do not invent a domain or a privacy-policy URL when packaging a separate extension release. For extension legal link updates, use your private extension release process; this website ZIP does not contain that private tooling.

### Production release checklist

- [ ] Review [SECURITY_DEPLOYMENT.md](SECURITY_DEPLOYMENT.md) and enable account MFA/passkeys and branch protections.
- [ ] Confirm that `vercel.json` applies the restrictive CSP and security headers on production responses.
- [ ] Confirm the website serves `public/` only; the monitoring scripts and release manifest must not be public URLs.
- [ ] Verify the GCash receiving QR and card still represent your intended receiving account; protect and monitor the hashes independently.
- [ ] Confirm that all pages and the production extension ZIP load over HTTPS.
- [ ] Recalculate the download's SHA-256 after a future extension release and update the guide checksum and independent manifest.
- [ ] Test the extension's links to the real published Privacy and Contact pages.
- [ ] Test desktop and mobile layouts, both color themes, keyboard navigation, and visible buttons.
- [ ] Review all privacy/security notices after any new payment, script, or storage behavior.

## Privacy and responsible use

QuestionForge's document extraction happens in the browser. It does **not automatically upload teaching materials** to AI chatbots or to the QuestionForge website. If you copy and paste extracted text into a third-party AI service, that content is then subject to that service's terms and privacy practices.

Question drafts may be stored in local Chrome extension storage when saving is enabled. They are not encrypted by QuestionForge. Disable saving or clear stored data when working with sensitive assessments, and remove student information from anything you share externally.

The website is static and has no account-registration or payment-processing system. Optional **GCash** support displays a public receiving QR; payments take place outside QuestionForge. Donations never unlock features. Visitors should confirm the recipient in GCash before transferring funds.

Read the full [Privacy Policy](public/privacy.html) before distributing the extension to a school or institution.

## Support and project links

- **Help and feedback:** [Contact & Support](public/contact.html)
- **Developer profile:** [GitHub — xf00889](https://github.com/xf00889)
- **Optional GCash support:** [Donate via GCash](public/contact.html#support-the-project)

When reporting a problem, include the QuestionForge and Chrome versions, steps to reproduce, and a screenshot **with private student or examination details removed**.

## Source availability and rights

This repository contains a publicly served website and an installable **bundled/minified extension release**. The editable extension source and its build tooling are maintained separately and are **not published here**. Minification reduces readability but cannot make client-side extension code secret.

No open-source license for the QuestionForge extension is granted by this repository. Please contact the developer before copying, modifying, or redistributing its code or brand assets.

QuestionForge is an independent project and is **not affiliated with AI providers, browser vendors, or GCash**.

---

<div align="center">
  <sub>© 2026 QuestionForge · Built to help teachers create better-organized assessments.</sub>
</div>


## Mobile experience update (v1.7)

The site now has improved mobile navigation, a swipeable product preview, tap-friendly buttons, compact help-page navigation, and responsive GCash support. See [MOBILE_UPDATE.md](MOBILE_UPDATE.md). No framework or build command is required.


## Typography (v2.1)

QuestionForge uses **Instrument Sans** (OFL-1.1) for display headings, body copy, and navigation, while technical labels retain the system monospace stack. Fonts are loaded from Google Fonts on the website; no font binaries are included in the repository. The privacy policy discloses the request to Google Fonts.

The font is optional for functionality: the site remains usable if a visitor blocks remote fonts.
