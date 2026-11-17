#!/usr/bin/env python3
"""Validate the latest prepared GitHub ZIP and render its metadata into the static site."""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
from pathlib import Path, PurePosixPath
import re
from urllib.request import Request, urlopen
import zipfile

MAX_ZIP = 16 * 1024 * 1024


def version_parts(version):
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:\.\d+)?", version):
        raise ValueError("Use a numeric Chrome version, e.g. 0.8.5, with a matching v0.8.5 release tag.")
    parts = tuple(int(part) for part in version.split('.'))
    if any(part > 65535 or str(int(raw)) != raw for part, raw in zip(parts, version.split('.'))):
        raise ValueError("Invalid Chrome version components.")
    return parts + (0,) * (4 - len(parts))


def asset_name(version):
    return f'QuestionForge-v{version}-production.zip'


def validate_metadata(data):
    version_parts(data['version'])
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', data['repository']):
        raise ValueError('Invalid GitHub owner/repository.')
    if not re.fullmatch(r'[a-f0-9]{64}', data['sha256']):
        raise ValueError('Invalid SHA-256 checksum.')
    if type(data['size_bytes']) is not int or not 0 < data['size_bytes'] <= MAX_ZIP:
        raise ValueError('Release ZIP must be between 1 byte and 16 MiB.')
    if type(data['prerelease']) is not bool:
        raise ValueError('prerelease must be a boolean.')
    filename = asset_name(data['version'])
    allowed = (
        f'downloads/{filename}',
        f'https://github.com/{data["repository"]}/releases/download/v{data["version"]}/{filename}',
    )
    if data['download_url'] not in allowed:
        raise ValueError('Download must be the matching local fallback or a version-pinned GitHub release asset.')


def validate_zip(raw, version):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or any(
            '\\' in name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts
            for name in names
        ):
            raise ValueError('ZIP contains duplicate or unsafe paths.')
        manifests = [name for name in names if PurePosixPath(name).name == 'manifest.json'
                     and len(PurePosixPath(name).parts) <= 2]
        if len(manifests) != 1:
            raise ValueError('ZIP must contain one extension manifest at its root or inside one folder.')
        with archive.open(manifests[0]) as entry:
            manifest_raw = entry.read(65537)
        if len(manifest_raw) > 65536:
            raise ValueError('Extension manifest is too large.')
        manifest = json.loads(manifest_raw)
        if manifest.get('manifest_version') != 3 or manifest.get('version') != version:
            raise ValueError('ZIP manifest version does not match the release tag.')
        if 'QuestionForge' not in manifest.get('name', ''):
            raise ValueError('ZIP is not a QuestionForge extension.')
        base = PurePosixPath(manifests[0]).parent
        for filename in (manifest['side_panel']['default_path'], manifest['background']['service_worker']):
            path = PurePosixPath(filename)
            if path.is_absolute() or '..' in path.parts or str(base / path) not in names:
                raise ValueError('ZIP is missing a declared runtime entry point.')


def fetch(url, limit):
    accept = 'application/vnd.github+json' if url.startswith('https://api.github.com/') else 'application/octet-stream'
    request = Request(url, headers={'User-Agent': 'QuestionForge-Release-Sync', 'Accept': accept})
    with urlopen(request, timeout=60) as response:
        if not response.url.startswith('https://'):
            raise ValueError('Release fetch redirected outside HTTPS.')
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Release response exceeds the permitted size.')
    return raw


def latest_release(current):
    releases = json.loads(fetch(f'https://api.github.com/repos/{current["repository"]}/releases?per_page=100', 2 * 1024 * 1024))
    if not isinstance(releases, list):
        raise ValueError('GitHub returned an invalid release list.')
    published = [release for release in releases if not release.get('draft') and release.get('published_at')]
    if not published:
        print('No published GitHub release yet; keeping the current verified download.')
        return current
    # shortcut: inspect the newest 100 releases; paginate if release history needs to exceed this window.
    release = max(published, key=lambda item: version_parts(item['tag_name'].removeprefix('v')))
    version = release['tag_name'].removeprefix('v')
    if release['tag_name'] != f'v{version}':
        raise ValueError('Release tags must use vVERSION.')
    if version_parts(version) < version_parts(current['version']):
        print(f'GitHub v{version} is older than the verified v{current["version"]} download; keeping the current download.')
        return current
    matches = [asset for asset in release['assets'] if asset['name'] == asset_name(version)]
    if len(matches) != 1 or matches[0].get('state') != 'uploaded':
        raise ValueError(f'Upload exactly one completed {asset_name(version)} asset before publishing the release.')
    asset = matches[0]
    result = {
        'repository': current['repository'], 'version': version,
        'download_url': asset['browser_download_url'], 'size_bytes': asset['size'],
        'sha256': '0' * 64, 'prerelease': release['prerelease'],
    }
    validate_metadata(result)
    raw = fetch(result['download_url'], MAX_ZIP)
    result['sha256'] = hashlib.sha256(raw).hexdigest()
    if len(raw) != result['size_bytes']:
        raise ValueError('Downloaded ZIP size differs from GitHub release metadata.')
    if asset.get('digest') and asset['digest'] != 'sha256:' + result['sha256']:
        raise ValueError('Downloaded ZIP does not match GitHub SHA-256 metadata.')
    if version_parts(version) == version_parts(current['version']) and result['sha256'] != current['sha256']:
        raise ValueError('An existing version was replaced with different bytes. Publish a new version instead.')
    validate_zip(raw, version)
    return result


def attribute(tag, name, value):
    result, count = re.subn(rf'\b{re.escape(name)}="[^"]*"', f'{name}="{html.escape(value, quote=True)}"', tag)
    if count != 1:
        raise ValueError(f'Marked release element must contain one {name} attribute.')
    return result


def render(text, release):
    values = {
        'version': 'v' + release['version'],
        'badge': 'v' + release['version'] + (' Beta' if release['prerelease'] else ''),
        'size': f'{release["size_bytes"] / 1024:.1f} KB',
        'sha256': release['sha256'],
    }
    pattern = r'(?P<open><(?P<tag>span|code)\b[^>]*\bdata-release="(?P<key>version|badge|size|sha256)"[^>]*>)[^<]*(?P<close></(?P=tag)>)'
    text = re.sub(pattern, lambda m: m['open'] + html.escape(values[m['key']]) + m['close'], text)
    text = re.sub(r'<a\b[^>]*\bdata-release="download"[^>]*>',
                  lambda m: attribute(m[0], 'href', release['download_url']), text)
    return re.sub(r'<button\b[^>]*\bdata-release="copy-hash"[^>]*>',
                  lambda m: attribute(m[0], 'data-copy-hash', release['sha256']), text)


def sync(root, use_latest=False):
    metadata_path = root / 'public/release.json'
    current = json.loads(metadata_path.read_text(encoding='utf-8'))
    validate_metadata(current)
    if current['download_url'].startswith('downloads/'):
        raw = (root / 'public' / current['download_url']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != current['sha256'] or len(raw) != current['size_bytes']:
            raise ValueError('Current local fallback ZIP differs from its release metadata.')
        validate_zip(raw, current['version'])
    release = latest_release(current) if use_latest else current
    outputs = {metadata_path: (json.dumps(release, indent=2) + '\n').encode()}
    for page in (root / 'public').glob('*.html'):
        text = page.read_text(encoding='utf-8')
        required = ['badge', 'version'] + (['download', 'size', 'sha256', 'copy-hash'] if page.name == 'guide.html' else [])
        if any(f'data-release="{field}"' not in text for field in required):
            raise ValueError(f'{page.name}: missing release metadata marker.')
        outputs[page] = render(text, release).encode()
        mirror = root / page.name
        if mirror.exists():
            outputs[mirror] = render(mirror.read_text(encoding='utf-8'), release).encode()
    manifest_path = root / 'release-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    entries = {entry['path']: entry['sha256'] for entry in manifest['files']}
    for path, raw in outputs.items():
        if path.is_relative_to(root / 'public'):
            entries[path.relative_to(root / 'public').as_posix()] = hashlib.sha256(raw).hexdigest()
    manifest['files'] = [{'path': name, 'sha256': digest} for name, digest in sorted(entries.items())]
    outputs[manifest_path] = (json.dumps(manifest, indent=2) + '\n').encode()
    for path, raw in outputs.items():
        if path.read_bytes() != raw:
            path.write_bytes(raw)
    print(f'Ready: v{release["version"]} | {release["download_url"]} | SHA-256 {release["sha256"]}')
    return release


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--latest', action='store_true', help='Fetch the newest published GitHub release, including prereleases.')
    args = parser.parse_args()
    try:
        sync(args.root.resolve(), args.latest)
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Release sync failed: {error}\n')
