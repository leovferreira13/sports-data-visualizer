"""Scoped local tracked/build content review; not a formal privacy guarantee."""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    envelope = json.loads((root / 'model/selected-model.json').read_text())
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    tracked = [root / p for p in tracked if p]
    assets = [p for p in (root / '.next/static').rglob('*') if p.is_file()]
    assets += [p for p in (root / '.next/server/app').rglob('*') if p.is_file()]
    forbidden_paths = []
    findings = []
    embedded = []
    strong_record = re.compile(r'"(?:shot_id|event_id)"\s*:\s*"[^"\n]+"|"(?:label|is_goal)"\s*:\s*(?:0|1|true|false)\s*,\s*"vector"\s*:\s*\[')
    for path in tracked:
        relative = path.relative_to(root).as_posix()
        if relative.startswith(('data/', 'downloads/', 'notebooks/', 'artifacts/')) or path.suffix in ('.parquet', '.csv', '.jsonl', '.ipynb'):
            forbidden_paths.append(relative)
        # Source-shaped schema/code and declared invented fixtures are not source records.
        if path.suffix == '.json' and not relative.startswith('tests/fixtures/'):
            data = json.loads(path.read_text())
            def inspect(value):
                if isinstance(value, dict):
                    if ('vector' in value and ('label' in value or 'shot_id' in value)) or ('timestamp' in value and 'id' in value and 'shot' in value):
                        findings.append(relative)
                    for child in value.values():
                        inspect(child)
                elif isinstance(value, list):
                    for child in value:
                        inspect(child)
            inspect(data)
    for path in assets:
        if path.suffix not in ('.js', '.json', '.html', '.rsc', '.txt'):
            continue
        text = path.read_text(errors='replace')
        if strong_record.search(text):
            findings.append(path.relative_to(root).as_posix())
    assert not forbidden_paths, forbidden_paths
    assert not findings, findings
    asset = root / 'public/model/selected-model.json'
    raw = asset.read_bytes()
    original = (root / 'model/selected-model.json').read_bytes()
    assert raw == original, 'Static model bytes differ from reviewed source'
    embedded = [{'path': 'public/model/selected-model.json', 'bytes': len(raw),
                 'gzip_bytes': len(gzip.compress(raw, mtime=0)), 'sha256': hashlib.sha256(raw).hexdigest()}]
    rights = json.loads((root / 'docs/reports/xg-artifact-distribution-review.json').read_text())
    assert embedded[0]['sha256'] == rights['file_sha256']
    assert json.loads(raw) == envelope
    report = {'schema_version': 1, 'build_id': (root / '.next/BUILD_ID').read_text().strip(),
              'base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
              'scope': 'current tracked paths/JSON and final static/prerendered production assets; prior history reviewed in #8',
              'tracked_files': len(tracked), 'build_assets': len(assets), 'embedded_model': embedded,
              'artifact_id': envelope['artifact_id'], 'forbidden_paths': forbidden_paths,
              'source_record_signatures': findings, 'status': 'PASS', 'publication_authorized': False}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
