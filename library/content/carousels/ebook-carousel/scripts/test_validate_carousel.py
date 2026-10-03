"""Synthetic, offline fixtures only; no production assets or network calls."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from validate_carousel import validate


def png(color, width=1080, height=1920):
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload +
                struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))
    pixels = (b'\0' + bytes(color) * width) * height
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b''))


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='carousel-validator-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / '005-fixture'
        for relative in ['README.md', 'qa.md', 'research/findings.md', 'research/candidates.md',
                         'research/tag-rationale.md', 'research/performance-review.md', 'idea/brief.md', 'idea/storyline.md',
                         'idea/funnel.md', 'idea/image-prompts.md',
                         'captions/instagram-description.txt', 'captions/tiktok-description.txt']:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Synthetic test fixture, not production content.\n')
        self.sources = {'queries': [{'provider': 'exa-mcp', 'query': 'fixture'}],
                        'sources': [{'id': 'P01', 'provider': 'exa-mcp',
                                     'url': 'https://publisher.example/',
                                     'observed_at': '2026-10-02T00:00:00Z',
                                     'access': 'fixture', 'supports': ['fixture']} ]}
        self.manifest = {
            'schema_version': 1, 'content_id': '005', 'format': 'carousel', 'status': 'draft',
            'merchant_hosts': ['publisher.example'], 'copy_revision': 'fixture-v1', 'publishing_routes': {'tiktok': 'unselected'},
            'product': {'title': 'Fixture', 'url': 'https://publisher.example/',
                        'observed_at': '2026-10-02T00:00:00Z', 'source_id': 'P01'},
            'funnel': {'destination_url': 'https://publisher.example/', 'platforms': {}},
            'publication_prerequisites': {'instagram': ['Check bio'], 'tiktok': ['Check bio']},
            'stages': {key: 'complete' for key in ['performance', 'research', 'writing', 'images', 'captions', 'review']},
            'review': {key: True for key in ['all_images_inspected', 'copy_verified', 'claims_verified',
                       'funnel_verified', 'reference_consistency', 'visual_variety', 'mobile_readability']},
            'slides': []}
        self.performance = {
            'observed_at': '2026-10-02T00:00:00Z',
            'window': {'from': '2026-09-02T00:00:00Z', 'to': '2026-10-02T00:00:00Z', 'timezone': 'UTC'},
            'platforms': {network: {'status': 'no_data', 'reason': 'Synthetic empty-history response',
                                   'attempted_at': '2026-10-02T00:00:00Z',
                                   'analysis': {'decision': 'skipped_unavailable', 'reason': 'fixture',
                                                'min_views_per_post': 100, 'min_comparable_posts': 3,
                                                'comparable_posts': 0}}
                          for network in ['instagram', 'tiktok']}}
        (self.root / 'exports').mkdir()
        self.add_slide((238, 233, 224))
        self.add_slide((52, 66, 54))
        for color in [(100, 110, 120), (130, 140, 150), (160, 170, 180)]:
            self.add_slide(color)
        self.save()

    def add_slide(self, color):
        number = len(self.manifest['slides']) + 1
        relative = f'exports/{number:02d}-fixture.png'
        data = png(color)
        (self.root / relative).write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        review_path = f'reviews/{number:02d}-review.json'
        review = self.root / review_path
        review.parent.mkdir(exist_ok=True)
        review.write_text(json.dumps({'path': relative, 'sha256': digest, 'verdict': 'pass',
                                     'reviewer': 'synthetic-reviewer', 'copy_revision': 'fixture-v1',
                                     'inspected_at': '2026-10-02T00:00:00Z',
                                     'full_resolution_checked': True, 'phone_scale_checked': True}))
        self.manifest['slides'].append({'path': relative, 'sha256': digest, 'review_path': review_path})

    def save(self):
        (self.root / 'run.json').write_text(json.dumps(self.manifest))
        (self.root / 'research/sources.json').write_text(json.dumps(self.sources))
        (self.root / 'research/performance.json').write_text(json.dumps(self.performance))

    def test_missing_performance_snapshot(self):
        (self.root / 'research/performance.json').unlink()
        self.assertTrue(any('performance.json' in e for e in validate(self.root)))

    def test_unsupported_performance_success(self):
        self.performance['platforms']['instagram']['status'] = 'ok'
        self.save()
        self.assertTrue(any('rows/metric definitions' in e for e in validate(self.root)))

    def test_unexplained_performance_gap(self):
        del self.performance['platforms']['tiktok']['reason']
        self.save()
        self.assertTrue(any('limitation reason' in e for e in validate(self.root)))

    def test_four_slides_rejected(self):
        self.manifest['slides'].pop()
        self.save()
        self.assertTrue(any('5–6 slides' in e for e in validate(self.root)))

    def test_malformed_performance_rows(self):
        report = self.performance['platforms']['instagram']
        report.update(status='ok', metrics=[{'fieldId': 'example', 'metricName': 'views'}])
        for rows in ['invalid', [['1', 'extra']]]:
            report['rows'] = rows
            self.save()
            self.assertTrue(any('rows/metric definitions' in e for e in validate(self.root)))

    def test_valid_performance_rows(self):
        self.performance['platforms']['instagram'].update(
            status='ok', metrics=[{'fieldId': 'example', 'metricName': 'views'}], rows=[['0']])
        self.save()
        self.assertEqual(validate(self.root), [])

    def test_complete_fixture(self):
        self.assertEqual(validate(self.root), [])

    def test_folder_delivery_without_zip(self):
        self.assertFalse(list((self.root / 'exports').glob('*.zip')))
        self.assertEqual(validate(self.root), [])

    def test_empty_caption(self):
        (self.root / 'captions/instagram-description.txt').write_text('   ')
        self.assertTrue(any('Empty caption' in e for e in validate(self.root)))

    def test_seven_slides(self):
        for i in range(2): self.add_slide((i, i, i))
        self.save()
        self.assertTrue(any('5–6' in e for e in validate(self.root)))

    def test_duplicate_images(self):
        self.add_slide((238, 233, 224))
        self.save()
        self.assertIn('Exact duplicate slides detected', validate(self.root))

    def test_missing_exa(self):
        self.sources['queries'] = []
        self.save()
        self.assertTrue(any('Exa MCP' in e for e in validate(self.root)))

    def test_independent_platform_bio_checks(self):
        self.manifest['funnel']['platforms']['instagram'] = {
            'bio_link_verified': True, 'account': 'test',
            'observed_url': 'https://publisher.example/', 'observed_at': '2026-10-02T00:00:00Z'}
        self.manifest['publication_prerequisites'] = {}
        self.save()
        failures = validate(self.root)
        self.assertTrue(any('prerequisite: tiktok' in e for e in failures))
        self.assertFalse(any('prerequisite: instagram' in e for e in failures))

    def test_malformed_png(self):
        path = self.root / self.manifest['slides'][0]['path']
        path.write_bytes(b'not an image')
        self.manifest['slides'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        self.assertTrue(any('not a PNG' in e for e in validate(self.root)))

    def test_path_escape(self):
        self.manifest['slides'][0]['path'] = '../outside.png'
        self.save()
        self.assertTrue(any('path escapes project' in e for e in validate(self.root)))

    def test_stale_slide_review(self):
        slide = self.manifest['slides'][0]
        path = self.root / slide['path']
        path.write_bytes(png((100, 100, 100)))
        slide['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save()
        self.assertTrue(any('Stale or mismatched' in e for e in validate(self.root)))

    def test_missing_phone_review(self):
        path = self.root / self.manifest['slides'][0]['review_path']
        review = json.loads(path.read_text())
        review['phone_scale_checked'] = False
        path.write_text(json.dumps(review))
        self.assertTrue(any('Incomplete image review' in e for e in validate(self.root)))

    def test_changed_copy_invalidates_review(self):
        self.manifest['copy_revision'] = 'fixture-v2'
        self.save()
        self.assertTrue(any('copy revision mismatch' in e for e in validate(self.root)))

    def test_api_route_requires_jpeg_set(self):
        self.manifest['publishing_routes']['tiktok'] = 'api'
        self.save()
        self.assertTrue(any('complete JPEG' in e for e in validate(self.root)))

    def test_valid_api_set_and_stale_jpeg_review(self):
        from PIL import Image
        self.manifest['publishing_routes']['tiktok'] = 'api'
        folder = self.root / 'exports/tiktok'
        folder.mkdir()
        entries = []
        for n, slide in enumerate(self.manifest['slides'], 1):
            relative = f'exports/tiktok/{n:02d}-fixture.jpg'
            path = self.root / relative
            with Image.open(self.root / slide['path']) as image:
                image.save(path, format='JPEG')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            review_path = f'reviews/{n:02d}-tiktok-review.json'
            review = json.loads((self.root / slide['review_path']).read_text())
            review.update(path=relative, sha256=digest)
            (self.root / review_path).write_text(json.dumps(review))
            entries.append({'path': relative, 'sha256': digest,
                            'source_sha256': slide['sha256'], 'review_path': review_path})
        self.manifest['delivery_sets'] = {'tiktok': {'format': 'jpeg', 'slides': entries}}
        self.save()
        self.assertEqual(validate(self.root), [])
        path = self.root / entries[0]['review_path']
        review = json.loads(path.read_text())
        review['sha256'] = 'stale'
        path.write_text(json.dumps(review))
        self.assertTrue(any('Stale or mismatched' in e for e in validate(self.root)))

    def test_missing_triage_decision(self):
        del self.performance['platforms']['instagram']['analysis']
        self.save()
        self.assertTrue(any('triage decision' in e for e in validate(self.root)))

    def test_mismatched_export_profile(self):
        self.manifest['export_profile'] = {'width': 1200, 'height': 1500}
        self.save()
        self.assertTrue(any('dimensions differ from export profile' in e for e in validate(self.root)))

    def test_unreviewed(self):
        self.manifest['review']['all_images_inspected'] = False
        self.save()
        self.assertTrue(any('all_images_inspected' in e for e in validate(self.root)))


if __name__ == '__main__':
    unittest.main()
