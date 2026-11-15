# QuestionForge production distribution — v0.8.4

The website downloads a bundled/minified **runtime-only** Chrome extension.
No development source modules, build scripts, source maps, tests, or examples are included in the public ZIP.

- Download: `downloads/QuestionForge-v0.8.4-production.zip`
- SHA-256: `3d93029424ab3ac1bc9cec05254ea4c1a62a54fce418a65a607aa650bf0a66f8`
- Extension manifest version: `0.8.3`
- Private repository: keep it private. Do not copy the private extension source into this website repository.
- Chrome Web Store: minification and bundling are allowed; intentional code obfuscation is not.

## Installation
Extract the ZIP. In `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select the `questionforge-extension` folder.

The ZIP is not CRX-signed and has not been uploaded to the Chrome Web Store.
The files remain inspectable, so do not place secrets or private keys in the extension.
