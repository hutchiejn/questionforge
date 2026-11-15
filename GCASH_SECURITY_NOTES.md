# GCash-only donations — QuestionForge website / extension

- Donation is completely voluntary; no feature is restricted or unlocked after paying.
- Website displays locally bundled QR and original receiving card, and neither embeds GCash nor connects to a payment API.
- Extension checks locally bundled QR and receiving card against shipped SHA-256 hashes, then displays the QR without contacting third-party servers. A matching hash alone is NOT proof of authenticity if an attacker can alter both files.
- The website's receiving card is publicly accessible; the user must verify the intended account details inside GCash before publishing. Public QR codes may reveal the recipient's identifying information when scanned.
- Source QR pixels are unchanged. The only adjustments are a lossless PNG conversion of the user-supplied JPEG and a crop of the QR rectangle for better visibility. No QR payload or recipient details were rewritten.
- Website visitors can download the full receiving card. The website does not verify, collect, or log donations (hosting provider may keep normal access logs).
- Extension's startup reminder can be declined or permanently disabled.
- Test the QR by scanning with the official GCash app and checking the recipient, without completing a payment.
- Check the local extension package and payment QR before sharing publicly. Publishing is NOT done by this package.
