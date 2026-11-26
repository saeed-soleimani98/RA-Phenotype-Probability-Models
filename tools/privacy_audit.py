#!/usr/bin/env python3
"""Data-free privacy/disclosure audit for this repository.

Inventories tracked files, scans source/notebook text for likely disclosures,
checks notebook state, and scans the complete Git history. No clinical data are
read or requested.

Usage: python tools/privacy_audit.py [--json OUT.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1_048_576  # owner-approved threshold placeholder; see PRIVACY_AUDIT_REPORT.md

PROHIBITED_EXT = {
    '.csv', '.tsv', '.xlsx', '.xls', '.parquet', '.feather', '.arrow',
    '.h5', '.hdf5', '.pkl', '.pickle', '.joblib', '.npy', '.npz',
    '.onnx', '.pt', '.pth', '.ckpt', '.safetensors', '.zip', '.tar', '.gz', '.7z',
}
TSV_ALLOW = {
    'FILE_MANIFEST.tsv',
    'docs/ORIGINAL_SOURCE_FILE_MANIFEST.tsv',
    'docs/FILE_INVENTORY_SHA256.tsv',
}
FORBIDDEN_NAME_TERMS = [
    'raw_data', 'cleaned_data', 'derived_data', 'patient_level',
    'predictions', 'fold_assignments', 'shap_values',
]
DOC_PREFIXES = ('docs/', 'archive/', '.github/')

PATTERNS = {
    'email': re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
    'token': re.compile(
        r'(?:ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|'
        r'api[_-]?key\s*[:=]\s*["\'][^"\']{8,}|password\s*[:=]\s*["\'][^"\']{4,}|'
        r'Bearer\s+[A-Za-z0-9._-]{12,})', re.I),
    'signed_url': re.compile(r'[?&](?:X-Goog-|sig=|token=|AWSAccessKeyId|Signature=)'),
    'private_url': re.compile(r'https?://(?:drive|docs)\.google\.com/[^\s"\'<>]+'),
    'absolute_path': re.compile(r'(?<![A-Za-z])[A-Za-z]:\\(?![nrt"])|/(?:home|Users|mnt|Volumes)/[^\s"\'<>]+'),
    'visitid_value': re.compile(r'VisitID\s*[:=]?\s*\d{3,}'),
    'base64_blob': re.compile(r'(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{240,}={0,2}(?![A-Za-z0-9+/])'),
}

TEXT_SUFFIXES = {'.py', '.md', '.ipynb', '.yaml', '.yml', '.txt', '.json', '.cff', '.example', '.env'}


def tracked() -> list[str]:
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files'], capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return ''


def scan_worktree(files: list[str]) -> dict:
    findings: list[dict] = []
    inventory: list[dict] = []
    notebooks = 0
    for rel in files:
        path = ROOT / rel
        if not path.is_file():
            continue
        size = path.stat().st_size
        mime = mimetypes.guess_type(rel)[0] or 'text/plain'
        inventory.append({'path': rel, 'mime': mime, 'size_bytes': size, 'sha256': sha256(path)})
        if size > MAX_BYTES:
            findings.append({'kind': 'oversize', 'path': rel, 'detail': f'{size} > {MAX_BYTES} bytes'})
        suffix = Path(rel).suffix.lower()
        if suffix in PROHIBITED_EXT and rel not in TSV_ALLOW:
            findings.append({'kind': 'prohibited_extension', 'path': rel, 'detail': suffix})
        low = rel.lower()
        if not (low.startswith(DOC_PREFIXES) or low.startswith('.gitignore')):
            for term in FORBIDDEN_NAME_TERMS:
                if term in low:
                    findings.append({'kind': 'forbidden_filename_term', 'path': rel, 'detail': term})
        if suffix == '.ipynb':
            notebooks += 1
            try:
                nb = json.loads(read_text(path))
            except json.JSONDecodeError as exc:
                findings.append({'kind': 'invalid_notebook', 'path': rel, 'detail': str(exc)})
                continue
            for i, cell in enumerate(nb.get('cells', [])):
                if cell.get('outputs'):
                    findings.append({'kind': 'notebook_output', 'path': rel, 'detail': f'cell {i}'})
                if cell.get('execution_count') is not None:
                    findings.append({'kind': 'execution_count', 'path': rel, 'detail': f'cell {i}'})
        if suffix in TEXT_SUFFIXES or rel in TSV_ALLOW or rel == '.gitignore':
            text = read_text(path)
            if suffix == '.ipynb':
                try:
                    nb = json.loads(text)
                    text = '\n'.join(''.join(c.get('source', [])) for c in nb.get('cells', []))
                except json.JSONDecodeError:
                    pass
            for label, pattern in PATTERNS.items():
                for m in pattern.finditer(text):
                    snippet = m.group(0)[:100]
                    # Documentation may legitimately describe exclusions and placeholders.
                    if label == 'absolute_path' and (
                        rel.startswith('docs/') or rel.startswith('tests/')
                        or rel == 'config/PATH_CONFIGURATION.md'
                        or rel == 'PRIVACY_AUDIT_REPORT.md'
                    ):
                        continue
                    findings.append({'kind': label, 'path': rel, 'detail': snippet})
    return {'inventory': inventory, 'findings': findings, 'notebooks_checked': notebooks}


def scan_history() -> dict:
    findings: list[dict] = []
    commits = subprocess.run(
        ['git', '-C', str(ROOT), 'log', '--all', '--format=%H'],
        capture_output=True, text=True, check=True).stdout.splitlines()
    for commit in commits:
        names = subprocess.run(
            ['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only', commit],
            capture_output=True, text=True, check=True).stdout.splitlines()
        for rel in names:
            suffix = Path(rel).suffix.lower()
            if suffix in PROHIBITED_EXT and rel not in TSV_ALLOW:
                findings.append({'kind': 'history_prohibited_extension', 'commit': commit[:12],
                                 'path': rel, 'detail': suffix})
            low = rel.lower()
            if not low.startswith(DOC_PREFIXES):
                for term in FORBIDDEN_NAME_TERMS:
                    if term in low:
                        findings.append({'kind': 'history_forbidden_filename_term',
                                         'commit': commit[:12], 'path': rel, 'detail': term})
    return {'commits_scanned': len(commits), 'findings': findings}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', type=Path, help='Write full machine-readable report here')
    args = ap.parse_args()

    files = tracked()
    work = scan_worktree(files)
    hist = scan_history()
    lfs = (ROOT / '.gitattributes').exists() and 'filter=lfs' in (ROOT / '.gitattributes').read_text()
    report = {
        'repository': str(ROOT),
        'tracked_files': len(files),
        'worktree': work,
        'history': hist,
        'git_lfs_used': lfs,
        'status': 'PASS' if not work['findings'] and not hist['findings'] and not lfs else 'REVIEW REQUIRED',
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2), encoding='utf-8')

    print(f"status={report['status']}")
    print(f"tracked_files={len(files)} notebooks_checked={work['notebooks_checked']} "
          f"commits_scanned={hist['commits_scanned']} git_lfs={lfs}")
    print(f"worktree_findings={len(work['findings'])} history_findings={len(hist['findings'])}")
    for f in (work['findings'] + hist['findings'])[:50]:
        print(' -', f)
    if report['status'] != 'PASS':
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
