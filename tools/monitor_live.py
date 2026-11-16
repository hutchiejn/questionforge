#!/usr/bin/env python3
"""Verify an HTTPS Vercel site against a trusted *offline* release manifest.

Run this script OUTSIDE the website deployment and store the manifest in
an independent location (ideally a separate private monitoring repository).
Exit code 1 = mismatch, header loss, unexpected redirect, or retrieval error.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen

CRITICAL=('assets/gcash-receive-qr.png','assets/gcash-receive-card.png','contact.html')
EXPECTED_HEADERS=('content-security-policy','x-content-type-options','x-frame-options','referrer-policy')

def fetch(base:str, path:str):
    url=base.rstrip('/')+'/'+quote(path,safe='/')
    req=Request(url,headers={'User-Agent':'QuestionForge-Independent-Integrity-Monitor/1.0','Cache-Control':'no-cache'})
    with urlopen(req,timeout=20) as r:
        final=urlparse(r.url)
        if final.scheme!='https' or final.netloc != urlparse(base).netloc:
            raise RuntimeError(f'Unexpected redirect for {path}: {r.url}')
        size=int(r.headers.get('content-length','0'))
        if size>16*1024*1024:raise RuntimeError(f'File exceeds permitted size: {path}')
        raw=r.read(16*1024*1024+1)
        if len(raw)>16*1024*1024:raise RuntimeError(f'File too large: {path}')
        return raw,r.headers

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--site',required=True,help='Canonical public HTTPS origin, e.g. https://example.vercel.app')
    ap.add_argument('--manifest',type=Path,required=True,help='Trusted manifest stored outside the site repo')
    a=ap.parse_args()
    u=urlparse(a.site)
    if u.scheme!='https' or not u.netloc or u.username or u.password or u.path not in ('','/') or u.query or u.fragment:
        ap.error('--site must be a public canonical HTTPS origin with no path or credentials')
    manifest=json.loads(a.manifest.read_text(encoding='utf-8'))
    items={x['path']:x['sha256'] for x in manifest['files']}
    errors=[]
    if not all(x in items for x in CRITICAL):
        errors.append('Missing critical assets/contact page in the trusted manifest')
    for path, expected in items.items():
        try:
            raw,headers=fetch(a.site,path)
            actual=hashlib.sha256(raw).hexdigest()
            if actual!=expected:
                errors.append(f'{path}: SHA-256 CHANGED (expected {expected}, got {actual})')
            if path.endswith('.html'):
                for h in EXPECTED_HEADERS:
                    if not headers.get(h):errors.append(f'{path}: missing HTTP security header {h}')
                csp=headers.get('content-security-policy','')
                for fragment in ("script-src 'self'","frame-ancestors 'none'","object-src 'none'","style-src-attr 'none'"):
                    if fragment not in csp:errors.append(f'{path}: CSP weakened: {fragment}')
            if path.endswith('gcash-receive-qr.png') and not raw.startswith(b'\x89PNG\r\n\x1a\n'):
                errors.append(f'{path}: not a PNG')
        except (HTTPError,URLError,RuntimeError,TimeoutError) as e:
            errors.append(f'{path}: retrieval failed: {e}')
    if errors:
        print('ALERT — QuestionForge live site verification FAILED')
        for msg in errors:print('  - '+msg)
        raise SystemExit(1)
    print(f'PASS — {len(items)} published files match the separately held trusted manifest; HTML security headers present.')

if __name__=='__main__':main()
