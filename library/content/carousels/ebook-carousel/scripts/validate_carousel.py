#!/usr/bin/env python3
"""Read-only structural validation; human/agent review remains necessary."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import urlparse
import zlib


def merchant_url(value, hosts):
    parsed = urlparse(value)
    return parsed.scheme == 'https' and bool(parsed.hostname) and parsed.hostname in hosts and not parsed.username and not parsed.password


def png_size(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('not a PNG')
    pos, dimensions, image_data, ended = 8, None, bytearray(), False
    while pos + 12 <= len(data):
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        stop = pos + 8 + size
        if stop + 4 > len(data):
            raise ValueError('truncated PNG chunk')
        payload = data[pos + 8:stop]
        checksum = struct.unpack('>I', data[stop:stop + 4])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != checksum:
            raise ValueError('PNG CRC mismatch')
        if kind == b'IHDR':
            if pos != 8 or size != 13:
                raise ValueError('invalid PNG header')
            dimensions = struct.unpack('>II', payload[:8])
        elif kind == b'IDAT':
            image_data.extend(payload)
        elif kind == b'IEND':
            ended = True
            break
        pos = stop + 4
    if not dimensions or not ended or not image_data:
        raise ValueError('incomplete PNG')
    if not zlib.decompress(image_data):
        raise ValueError('empty PNG pixel stream')
    return dimensions


def validate(root):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def local_file(relative):
        candidate = (root / relative).resolve()
        if not candidate.is_relative_to(root):
            raise ValueError('path escapes project: ' + relative)
        return candidate

    def check_review(relative, digest, review_path, prefix):
        require(bool(re.fullmatch(prefix + r'[a-z0-9-]+\.json', review_path)),
                'Slide review path/order invalid: ' + relative)
        try:
            review = json.loads(local_file(review_path).read_text())
            require(review.get('path') == relative and review.get('sha256') == digest,
                    'Stale or mismatched image review: ' + relative)
            require(bool(manifest.get('copy_revision')) and
                    review.get('copy_revision') == manifest.get('copy_revision'),
                    'Review copy revision mismatch: ' + relative)
            require(review.get('verdict') == 'pass' and
                    review.get('full_resolution_checked') is True and
                    review.get('phone_scale_checked') is True and
                    bool(review.get('reviewer')) and bool(review.get('inspected_at')),
                    'Incomplete image review: ' + relative)
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append('Invalid image review ' + relative + ': ' + str(exc))

    required = [
        'README.md', 'qa.md', 'research/sources.json', 'research/findings.md',
        'research/performance.json', 'research/performance-review.md',
        'research/candidates.md', 'research/tag-rationale.md', 'idea/brief.md',
        'idea/storyline.md', 'idea/funnel.md', 'idea/image-prompts.md',
        'captions/instagram-description.txt', 'captions/tiktok-description.txt',
    ]
    for name in required:
        path = local_file(name)
        require(path.is_file() and path.stat().st_size > 0, 'Missing/empty ' + name)
    try:
        manifest = json.loads(local_file('run.json').read_text())
        sources = json.loads(local_file('research/sources.json').read_text())
        performance = json.loads(local_file('research/performance.json').read_text())
    except (OSError, ValueError) as exc:
        return errors + ['Invalid manifest/source packet: ' + str(exc)]
    require(manifest.get('schema_version') == 1, 'schema_version must be 1')
    require(bool(performance.get('observed_at')), 'Performance observation time missing')
    require(all(performance.get('window', {}).get(k) for k in ['from', 'to', 'timezone']),
            'Performance query window missing')
    for platform in ['instagram', 'tiktok']:
        report = performance.get('platforms', {}).get(platform, {})
        require(report.get('status') in {'ok', 'no_data', 'unavailable'},
                'Performance coverage missing: ' + platform)
        require(bool(report.get('attempted_at')), 'Performance attempt time missing: ' + platform)
        analysis = report.get('analysis', {})
        require(analysis.get('decision') in {'analyze', 'skipped_low_views',
                'skipped_sparse_sample', 'skipped_unavailable'} and bool(analysis.get('reason')),
                'Performance triage decision/reason missing: ' + platform)
        require(all(isinstance(analysis.get(k), int) and analysis[k] >= 0
                    for k in ['min_views_per_post', 'min_comparable_posts', 'comparable_posts']),
                'Performance triage threshold/count missing: ' + platform)

        if report.get('status') == 'ok':
            rows, metrics = report.get('rows'), report.get('metrics')
            valid_metrics = isinstance(metrics, list) and bool(metrics) and all(
                isinstance(m, dict) and m.get('fieldId') and m.get('metricName') for m in metrics)
            valid_rows = isinstance(rows, list) and bool(rows) and valid_metrics and all(
                isinstance(row, list) and len(row) == len(metrics) for row in rows)
            require(valid_rows and valid_metrics,
                    'Performance rows/metric definitions missing: ' + platform)
        else:
            require(bool(report.get('reason')), 'Performance limitation reason missing: ' + platform)
    require(manifest.get('format') == 'carousel', 'format must be carousel')
    require(manifest.get('status') in {'draft', 'ready'}, 'Invalid production status for this workflow')
    require(re.fullmatch(r'\d{3}', str(manifest.get('content_id', ''))) is not None,
            'content_id must contain three digits')
    require(root.name.startswith(str(manifest.get('content_id')) + '-'),
            'Project directory must start with content_id-')
    entries = sources.get('sources', [])
    queries = sources.get('queries', [])
    require(any(s.get('provider') == 'exa-mcp' for s in entries) and
            any(q.get('provider') == 'exa-mcp' for q in queries),
            'Missing recorded live Exa MCP sources/queries')
    ids = [s.get('id') for s in entries]
    require(all(ids) and len(ids) == len(set(ids)), 'Source IDs missing or duplicated')
    for s in entries:
        require(bool(s.get('observed_at')) and bool(s.get('access')) and bool(s.get('supports')),
                'Source missing observation/access/supports: ' + str(s.get('id')))
        require(bool(s.get('url') or s.get('local_path')), 'Source has no locator: ' + str(s.get('id')))
    hosts = manifest.get('merchant_hosts', [])
    require(isinstance(hosts, list) and bool(hosts) and all(isinstance(h, str) and h for h in hosts),
            'Configured merchant_hosts missing')
    product = manifest.get('product', {})
    require(bool(product.get('title')) and bool(product.get('observed_at')), 'Product facts missing')
    require(merchant_url(product.get('url', ''), hosts), 'Product URL must be HTTPS on a configured merchant host')
    require(product.get('source_id') in ids, 'Product source_id does not resolve')
    funnel = manifest.get('funnel', {})
    require(merchant_url(funnel.get('destination_url', ''), hosts), 'Funnel URL must be HTTPS on a configured merchant host')
    for platform in ['instagram', 'tiktok']:
        profile = funnel.get('platforms', {}).get(platform, {})
        if profile.get('bio_link_verified') is True:
            require(bool(profile.get('account')) and bool(profile.get('observed_url')) and
                    bool(profile.get('observed_at')), 'Bio evidence missing: ' + platform)
        else:
            require(bool(manifest.get('publication_prerequisites', {}).get(platform)),
                    'Unverified bio link requires a publication prerequisite: ' + platform)
    for stage in ['performance', 'research', 'writing', 'images', 'captions', 'review']:
        require(manifest.get('stages', {}).get(stage) == 'complete', 'Incomplete stage: ' + stage)
    for field in ['all_images_inspected', 'copy_verified', 'claims_verified', 'funnel_verified',
                  'reference_consistency', 'visual_variety', 'mobile_readability']:
        require(manifest.get('review', {}).get(field) is True, 'Review not completed: ' + field)
    profile = manifest.get('export_profile', {'width': 1080, 'height': 1350})
    target = (profile.get('width'), profile.get('height'))
    require(all(isinstance(n, int) for n in target) and
            target[0] >= 1080 and target[1] >= 1350 and target[0] * 5 == target[1] * 4,
            'Invalid 4:5 export profile')
    slides = manifest.get('slides', [])
    require(2 <= len(slides) <= 6, 'Carousel requires 2–6 slides')
    hashes, dimensions, slide_paths = [], [], set()
    for number, slide in enumerate(slides, 1):
        relative = slide.get('path', '')
        require(re.fullmatch(r'exports/' + f'{number:02d}' + r'-[a-z0-9-]+\.png', relative) is not None,
                'Slide path/order invalid: ' + relative)
        slide_paths.add(relative)
        try:
            path = local_file(relative)
            data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            hashes.append(digest)
            require(digest == slide.get('sha256'), 'Slide digest mismatch: ' + relative)
            check_review(relative, digest, slide.get('review_path', ''),
                         r'reviews/' + f'{number:02d}' + '-')
            width, height = png_size(data)
            dimensions.append((width, height))
            require((width, height) == target, 'Slide dimensions differ from export profile: ' + relative)
        except (OSError, ValueError, zlib.error, struct.error) as exc:
            errors.append('Invalid slide ' + relative + ': ' + str(exc))
    require(len(hashes) == len(set(hashes)), 'Exact duplicate slides detected')
    require(len(set(dimensions)) <= 1, 'Slide dimensions differ')
    exported = {str(p.relative_to(root)) for p in (root / 'exports').glob('[0-9][0-9]-*.png')}
    require(exported == slide_paths, 'Exported slides differ from manifest')
    routes = manifest.get('publishing_routes', {})
    require(routes.get('tiktok') in {'api', 'native_app', 'unselected'},
            'Declare TikTok publishing route: api, native_app, or unselected')
    if routes.get('tiktok') == 'api':
        delivery = manifest.get('delivery_sets', {}).get('tiktok', {})
        entries = delivery.get('slides', [])
        require(delivery.get('format') == 'jpeg' and len(entries) == len(slides),
                'TikTok API requires a complete JPEG delivery set')
        for number, entry in enumerate(entries, 1):
            relative = entry.get('path', '')
            require(bool(re.fullmatch(r'exports/tiktok/' + f'{number:02d}' + r'-[a-z0-9-]+\.jpg', relative)),
                    'TikTok JPEG path/order invalid: ' + relative)
            try:
                from PIL import Image
                path = local_file(relative)
                data = path.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                require(digest == entry.get('sha256'), 'TikTok JPEG digest mismatch: ' + relative)
                require(len(data) <= 20_000_000, 'TikTok JPEG exceeds 20 MB: ' + relative)
                with Image.open(path) as im:
                    require(im.format == 'JPEG' and im.mode == 'RGB' and im.size == target,
                            'TikTok JPEG format/mode/dimensions invalid: ' + relative)
                    im.verify()
                require(number <= len(slides) and entry.get('source_sha256') == slides[number - 1].get('sha256'),
                        'TikTok delivery source mismatch: ' + relative)
                check_review(relative, digest, entry.get('review_path', ''),
                             r'reviews/' + f'{number:02d}' + '-tiktok-')
            except (ImportError, OSError, ValueError) as exc:
                errors.append('Invalid TikTok delivery ' + relative + ': ' + str(exc))
    for path in sorted((root / 'captions').glob('*.txt')):
        data = path.read_bytes()
        require(bool(data.strip()), 'Empty caption: ' + path.name)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.project.resolve())
    except (ValueError, TypeError, AttributeError) as exc:
        errors = ['Malformed project data: ' + str(exc)]
    if errors:
        print('\n'.join('FAIL: ' + e for e in errors))
        return 1
    print('PASS: artifact checks. Visual, factual and funnel review remain agent responsibilities.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
