#!/usr/bin/env python3
"""Static website hardening checks. Standard-library only.

This check catches mistakes; it does not prove a deployment is uncompromised.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse, unquote

REQUIRED = {
    'default-src': "'none'",
    'script-src': "'self'",
    'script-src-attr': "'none'",
    'style-src-attr': "'none'",
    'frame-ancestors': "'none'",
    'object-src': "'none'",
    'form-action': "'none'",
}
CRITICAL_ASSETS = ('assets/gcash-receive-qr.png', 'assets/gcash-receive-card.png')

class PageAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs=[]
        self.errors=[]
        self.scripts=[]
        self.inline_scripts=0
        self.script_open=False
        self.qr_images=[]
        self.card_downloads=[]

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if any(k.lower().startswith('on') for k in a):
            self.errors.append(f'Inline event handler on <{tag}>')
        if 'style' in a:
            self.errors.append(f'Inline style on <{tag}>')
        if tag == 'style':
            self.errors.append('Inline <style> element')
        if tag == 'script':
            self.script_open=True
            if 'src' not in a:
                self.errors.append('Inline <script> element')
            else:
                self.scripts.append(a['src'])
        if tag=='img' and 'gcash-scan-image' in a.get('class','').split():
            self.qr_images.append(a.get('src',''))
        if tag=='a' and 'gcash-download' in a.get('class','').split():
            self.card_downloads.append(a.get('href',''))
        if tag in {'img','script','link','a','source'}:
            raw=a.get('src') or a.get('href')
            if raw:self.refs.append((tag,raw))

    def handle_endtag(self,tag):
        if tag=='script':self.script_open=False


def audit(root:Path, manifest:Path, expected_qr:str|None, expected_card:str|None)->list[str]:
    errors=[]
    try: cfg=json.loads((root/'vercel.json').read_text())
    except Exception as e:return [f'vercel.json invalid: {e}']
    if cfg.get('outputDirectory')!='public':
        errors.append('Vercel outputDirectory must be public (private tools/docs must not be served).')
    hdr=next((h for h in cfg.get('headers',[]) if h.get('source')=='/(.*)'),{})
    values={h.get('key'):h.get('value') for h in hdr.get('headers',[])}
    csp=values.get('Content-Security-Policy','')
    for directive,value in REQUIRED.items():
        if not any(x.strip()==f'{directive} {value}' for x in csp.split(';')):
            errors.append(f'CSP missing or incorrect: {directive} {value}')
    for h in ('X-Content-Type-Options','X-Frame-Options','Referrer-Policy'):
        if not values.get(h):errors.append(f'Missing HTTP header: {h}')
    public=root/'public'
    if not public.is_dir():return errors+['public/ does not exist']
    pages=list(public.glob('*.html'))
    if not pages:errors.append('No public HTML pages')
    for page in pages:
        scan=PageAudit()
        scan.feed(page.read_text(encoding='utf-8'))
        errors.extend(f'{page.name}: {e}' for e in scan.errors)
        for tag, ref in scan.refs:
            if ref.startswith(('mailto:','tel:','#')):continue
            u=urlparse(ref)
            if u.scheme in ('http','https'):
                if tag in ('img','script') or (tag=='link' and u.netloc not in ('fonts.googleapis.com','fonts.gstatic.com')):
                    errors.append(f'{page.name}: unexpected external resource {ref}')
                continue
            if u.scheme:continue
            path=unquote(u.path)
            if not path:continue
            target=public/path.lstrip('/') if path.startswith('/') else page.parent/path
            if not target.exists():errors.append(f'{page.name}: missing {ref}')
        if page.name=='contact.html':
            if scan.qr_images!=['assets/gcash-receive-qr.png']:
                errors.append('contact.html: QR preview path is missing/changed/duplicated')
            if scan.card_downloads!=['assets/gcash-receive-card.png']:
                errors.append('contact.html: receiving card download path is missing/changed/duplicated')
    if not manifest.exists():return errors+[f'Missing manifest at {manifest}']
    m=json.loads(manifest.read_text(encoding='utf-8'))
    listed={item['path']:item['sha256'] for item in m['files']}
    found={f.relative_to(public).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in public.rglob('*') if f.is_file()}
    for name in sorted(found.keys()^listed.keys()): errors.append(f'manifest file mismatch: {name}')
    for name in sorted(found.keys()&listed.keys()):
        if found[name]!=listed[name]:errors.append(f'manifest content mismatch: {name}')
    for name,digest in ((CRITICAL_ASSETS[0],expected_qr),(CRITICAL_ASSETS[1],expected_card)):
        if digest and found.get(name)!=digest.lower():errors.append(f'EXTERNAL BASELINE MISMATCH: {name}')
    # External baseline is deliberately optional locally, but mandatory in CI.
    return errors

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--expected-qr',help='Trusted hash from outside this repo')
    ap.add_argument('--expected-card',help='Trusted hash from outside this repo')
    ap.add_argument('--require-external-baseline',action='store_true')
    a=ap.parse_args()
    if a.require_external_baseline and (not a.expected_qr or not a.expected_card):
        ap.error('External QR and full-card SHA-256 values are required (GitHub repository variables, configured separately).')
    errs=audit(a.root,a.manifest or a.root/'release-manifest.json',a.expected_qr,a.expected_card)
    if errs:
        print('FAIL: '+str(len(errs))+' security audit finding(s)')
        for e in errs: print('  - '+e)
        raise SystemExit(1)
    print('PASS: static website audit, restrictive CSP, local links, and manifest digests')
    if not a.expected_qr or not a.expected_card:print('NOTE: no INDEPENDENT hash baseline was provided; local checks alone cannot detect a maliciously replaced manifest.')
