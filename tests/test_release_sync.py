import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('sync_release', Path(__file__).resolve().parents[1] / 'tools/sync_release.py')
release_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_sync)
REPOSITORY = 'xf00889/questionforge-ext'


def package(version='0.8.4', extra=None):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        manifest = {
            'manifest_version': 3, 'version': version, 'name': 'QuestionForge',
            'side_panel': {'default_path': 'sidepanel.html'},
            'background': {'service_worker': 'background.js'},
        }
        archive.writestr('questionforge-extension/manifest.json', json.dumps(manifest))
        archive.writestr('questionforge-extension/sidepanel.html', '<main>QuestionForge</main>')
        archive.writestr('questionforge-extension/background.js', '')
        if extra:
            archive.writestr(extra, 'unexpected')
    return output.getvalue()


def github_release(raw, version='0.8.5', prerelease=True):
    return {
        'tag_name': f'v{version}', 'draft': False, 'published_at': '2026-11-17T00:00:00Z',
        'prerelease': prerelease,
        'assets': [{
            'name': release_sync.asset_name(version), 'state': 'uploaded', 'size': len(raw),
            'browser_download_url': f'https://github.com/{REPOSITORY}/releases/download/v{version}/{release_sync.asset_name(version)}',
            'digest': 'sha256:' + hashlib.sha256(raw).hexdigest(),
        }],
    }


class ReleaseSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'public/downloads').mkdir(parents=True)
        raw = package()
        self.metadata = {
            'repository': REPOSITORY, 'version': '0.8.4',
            'download_url': 'downloads/QuestionForge-v0.8.4-production.zip',
            'size_bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'prerelease': True,
        }
        (self.root / 'public/release.json').write_text(json.dumps(self.metadata), encoding='utf-8')
        (self.root / 'public' / self.metadata['download_url']).write_bytes(raw)
        page = '''<span data-release="badge">v0.8.4 Beta</span>
<span data-release="version">v0.8.4</span>
<a data-release="download" href="downloads/QuestionForge-v0.8.4-production.zip">Download <span>ZIP</span></a>
<span data-release="size">594 KB</span>
<code data-release="sha256">old</code>
<button data-release="copy-hash" data-copy-hash="old">Copy hash</button>'''
        (self.root / 'public/guide.html').write_text(page, encoding='utf-8')
        (self.root / 'guide.html').write_text(page, encoding='utf-8')
        (self.root / 'public/privacy.html').write_text(
            '<span data-release="badge">v0.8.4 Beta</span>'
            '<span data-release="version">v0.8.4</span>'
            '<p>Policy reviewed for v0.8.4 on November 15, 2026.</p>', encoding='utf-8')
        (self.root / 'release-manifest.json').write_text(json.dumps({
            'schema': 1, 'files': [{'path': p.relative_to(self.root / 'public').as_posix(),
                                  'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                                 for p in (self.root / 'public').rglob('*') if p.is_file()],
        }), encoding='utf-8')

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def remote(self, release, raw):
        return patch.object(release_sync, 'fetch', side_effect=lambda url, limit:
                            json.dumps([release]).encode() if 'api.github.com' in url else raw)

    def test_new_prerelease_updates_download_checksum_mirrors_and_manifest(self):
        raw = package('0.8.5')
        with self.remote(github_release(raw), raw):
            result = release_sync.sync(self.root, True)
        page = (self.root / 'public/guide.html').read_text()
        self.assertIn(f'href="{result["download_url"]}"', page)
        self.assertIn('v0.8.5 Beta', page)
        self.assertIn(f'data-copy-hash="{result["sha256"]}"', page)
        self.assertIn(f'>{result["sha256"]}</code>', page)
        self.assertEqual((self.root / 'guide.html').read_bytes(), page.encode())
        self.assertIn('Policy reviewed for v0.8.4 on November 15, 2026.',
                      (self.root / 'public/privacy.html').read_text())
        manifest = json.loads((self.root / 'release-manifest.json').read_text())
        for entry in manifest['files']:
            self.assertEqual(entry['sha256'], hashlib.sha256((self.root / 'public' / entry['path']).read_bytes()).hexdigest())
        first = self.snapshot()
        with self.remote(github_release(raw), raw):
            release_sync.sync(self.root, True)
        self.assertEqual(first, self.snapshot())

    def test_no_releases_keeps_working_fallback(self):
        with patch.object(release_sync, 'fetch', return_value=b'[]'):
            result = release_sync.sync(self.root, True)
        self.assertEqual(result, self.metadata)
        self.assertIn('href="downloads/QuestionForge-v0.8.4-production.zip"',
                      (self.root / 'public/guide.html').read_text())

    def test_invalid_remote_release_never_changes_output(self):
        raw = package('0.8.5')
        cases = []
        for field, value in [('size', len(raw) + 1), ('digest', 'sha256:' + 'f' * 64),
                             ('browser_download_url', 'https://example.com/extension.zip'),
                             ('name', 'wrong.zip'), ('state', 'new')]:
            release = github_release(raw)
            release['assets'][0][field] = value
            cases.append((field, release, raw))
        cases.append(('wrong manifest version', github_release(package('0.8.3')), package('0.8.3')))
        cases.append(('replaced version', github_release(package('0.8.4', 'extra.txt'), '0.8.4'), package('0.8.4', 'extra.txt')))
        for label, release, contents in cases:
            with self.subTest(label=label):
                before = self.snapshot()
                with self.remote(release, contents), self.assertRaises(ValueError):
                    release_sync.sync(self.root, True)
                self.assertEqual(before, self.snapshot())

    def test_older_github_release_keeps_newer_verified_fallback(self):
        old_zip = package('0.8.2')
        with self.remote(github_release(old_zip, '0.8.2'), old_zip):
            result = release_sync.sync(self.root, True)
        self.assertEqual(result, self.metadata)

    def test_package_rejects_unsafe_paths(self):
        with self.assertRaisesRegex(ValueError, 'unsafe paths'):
            release_sync.validate_zip(package(extra='../outside.txt'), '0.8.4')

    def test_corrupt_local_fallback_is_rejected(self):
        (self.root / 'public' / self.metadata['download_url']).write_bytes(b'not the ZIP')
        with self.assertRaisesRegex(ValueError, 'fallback ZIP'):
            release_sync.sync(self.root)

    def test_missing_render_marker_does_not_write_partial_output(self):
        (self.root / 'public/guide.html').write_text('<h1>Install</h1>')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'missing release metadata marker'):
            release_sync.sync(self.root)
        self.assertEqual(before, self.snapshot())

    def test_unpinned_download_and_invalid_versions_are_rejected(self):
        for value in ['0.8', '0.8.5-beta', '0.08.5', '0.8.65536']:
            with self.subTest(version=value), self.assertRaises(ValueError):
                release_sync.version_parts(value)
        bad = dict(self.metadata, download_url=f'https://github.com/{REPOSITORY}/releases/latest/download/QuestionForge.zip')
        with self.assertRaisesRegex(ValueError, 'version-pinned'):
            release_sync.validate_metadata(bad)


if __name__ == '__main__':
    unittest.main()
