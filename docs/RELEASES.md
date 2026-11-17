# Publishing a QuestionForge download

The extension release repository is **https://github.com/xf00889/questionforge-ext**.
The website repository is **https://github.com/hutchiejn/questionforge**.

Upload the prepared production ZIP to a GitHub Release in the extension repository. Its release workflow calls a Vercel Deploy Hook. During the website build, `tools/sync_release.py --latest` checks the published package and updates the static pages and `public/release.json` together. Download URLs point to a specific version, so the displayed checksum belongs to that ZIP. Visitors do not call the GitHub API or need a GitHub account.

## One-time setup

1. Commit and push the website changes, including `vercel.json`, `public/release.json`, the HTML markers, `tools/sync_release.py`, and `.gitattributes`. Preserve the existing `public/` output directory in Vercel. The included build command runs release sync and the static security audit with Python 3.
2. Commit and push `.github/workflows/update-website.yml` in the extension repository to `main` **before creating the release tag**.
3. In the website's Vercel project, open **Settings → Git → Deploy Hooks**. Create a hook for the website's deployment branch, normally `main`.
4. In **xf00889/questionforge-ext → Settings → Secrets and variables → Actions**, add that URL as the repository secret **`VERCEL_DEPLOY_HOOK`**. The hook URL stays in GitHub secrets; do not commit it or put it in browser JavaScript.
5. Check that Vercel uses the build command from `vercel.json`, with no dashboard override. Keep the existing GCash checksum variables for the website's GitHub security gate.

## Each release

For example, to release version `0.8.5`:

1. Prepare the production ZIP using your existing packaging process. Its extension `manifest.json` must declare `"version": "0.8.5"`.
2. In the extension repository, draft a GitHub Release with tag **`v0.8.5`**.
3. Attach **`QuestionForge-v0.8.5-production.zip`**. The ZIP must contain the extension's manifest and declared runtime files, either at the archive root or inside one folder such as `questionforge-extension/`.
4. Publish the release **after the asset finishes uploading**. Mark developer-preview releases as prereleases if you want the website's Beta badge. Both normal releases and prereleases are supported.
5. Check **Actions → Update website download**, then the resulting Vercel deployment. The GitHub action confirms the hook request; the Vercel build logs confirm ZIP validation and website publication.

No new ZIP needs to be added to either website `downloads/` directory. The original v0.8.4 archive remains as the initial fallback; it can be retired separately after GitHub downloads are working.

The local extension source currently declares v0.8.2. This automation intentionally does not build or change that source. The prepared release ZIP's manifest determines the release version. You can publish the existing v0.8.4 production ZIP as the first release, provided it is byte-identical to the existing download.

## What is updated

- Header release badges and footer download-version labels.
- The install card's version, pinned ZIP link, file size, displayed SHA-256, and copy-checksum button.
- The FAQ's latest-release label.
- `public/release.json` and the integrity hashes of the generated files in `release-manifest.json`.

Privacy-policy applicability dates and the versions shown inside historical UI previews are not automatically changed by a package release. They need a content review when behavior or screenshots change.

Build-generated metadata is part of the deployed artifact; builds do not push commits back to either repository. When using `tools/monitor_live.py`, run `python tools/sync_release.py --latest` from the same website commit and archive the resulting `release-manifest.json` independently as the deployed release's baseline. A manifest from the unbuilt source checkout can describe the older fallback instead of the newly deployed GitHub release.

## Checks and recovery

```powershell
# Render the committed metadata without network requests:
python tools/sync_release.py

# Fetch and validate the current published release, then render it locally:
python tools/sync_release.py --latest

# Focused regression checks and the existing static audit:
python -m unittest discover -s tests -v
python tools/security_check.py
```

Until a GitHub release at or above the verified fallback version exists, the current local download remains available. Older GitHub releases are ignored. A missing asset, bad ZIP, mismatched tag/manifest, checksum mismatch, or network failure stops the new build; the previous successful Vercel deployment stays available. ZIPs are limited to 16 MiB. Use numeric Chrome versions and tags such as `v0.8.5`, and publish a new version for changed package bytes.

If a deployment did not start, run **Update website download → Run workflow** in the extension repository. For a failed deployment, fix the prepared release and publish a new version, or redeploy the previous known-good Vercel deployment.
