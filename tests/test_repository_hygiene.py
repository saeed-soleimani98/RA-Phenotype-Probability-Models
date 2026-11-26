"""Repository hygiene tests — static scanning only, no data access."""
from __future__ import annotations

import hashlib
import json
import py_compile
import re
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1_048_576
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
TEXT_SUFFIXES = {'.py', '.md', '.ipynb', '.yaml', '.yml', '.txt', '.json', '.cff'}


def tracked_files() -> list[str]:
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files'],
                         capture_output=True, text=True, check=True)
    files = out.stdout.splitlines()
    return files if files else [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts]


def test_all_python_files_compile(tmp_path):
    for path in ROOT.rglob('*.py'):
        if '.git' in path.parts:
            continue
        py_compile.compile(str(path), cfile=str(tmp_path / (path.stem + '.pyc')), doraise=True)


@pytest.mark.parametrize('rel', [f for f in tracked_files() if Path(f).suffix in {'.yaml', '.yml'}])
def test_yaml_files_parse(rel):
    yaml.safe_load((ROOT / rel).read_text(encoding='utf-8'))


def test_citation_cff_is_valid_yaml_and_uses_placeholders():
    data = yaml.safe_load((ROOT / 'CITATION.cff').read_text(encoding='utf-8'))
    assert data['cff-version'] == '1.2.0'
    assert 'OWNER_ACTION' in json.dumps(data), 'placeholder metadata should remain until owner completes it'


def test_no_prohibited_data_or_model_extensions():
    for rel in tracked_files():
        suffix = Path(rel).suffix.lower()
        if suffix in PROHIBITED_EXT:
            assert rel in TSV_ALLOW, f'prohibited tracked file: {rel}'


def test_no_forbidden_filename_terms_outside_documentation():
    for rel in tracked_files():
        low = rel.lower()
        if low.startswith(('docs/', 'archive/', '.github/')) or low == '.gitignore':
            continue
        for term in FORBIDDEN_NAME_TERMS:
            assert term not in low, f'{rel}: forbidden path term {term}'


def test_no_oversized_files():
    for rel in tracked_files():
        path = ROOT / rel
        if path.is_file():
            assert path.stat().st_size <= MAX_BYTES, f'{rel} exceeds size threshold'


def test_no_secrets_emails_or_private_links():
    patterns = {
        'email': re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
        'token': re.compile(r'(?:ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|Bearer\s+[A-Za-z0-9._-]{12,})', re.I),
        'private_drive_url': re.compile(r'https?://(?:drive|docs)\.google\.com/[^\s"\'<>]+'),
        'visitid_value': re.compile(r'VisitID\s*[:=]?\s*\d{3,}'),
    }
    for rel in tracked_files():
        path = ROOT / rel
        if Path(rel).suffix.lower() not in TEXT_SUFFIXES and rel != '.gitignore':
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        for label, pattern in patterns.items():
            for match in pattern.finditer(text):
                if label == 'email' and rel == 'docs/DATA_AVAILABILITY.md':
                    continue
                pytest.fail(f'{rel}: possible {label}: {match.group(0)[:80]}')


def test_no_absolute_private_paths_in_code_or_notebooks():
    for rel in tracked_files():
        if not rel.endswith(('.py', '.ipynb')):
            continue
        if rel.endswith('.ipynb'):
            nb = json.loads((ROOT / rel).read_text(encoding='utf-8', errors='ignore'))
            text = '\n'.join(''.join(c.get('source', [])) for c in nb['cells'])
        else:
            text = (ROOT / rel).read_text(encoding='utf-8', errors='ignore')
        assert '/' + 'home/user' not in text, f'{rel}: absolute private path'
        assert '/content/drive/' + 'MyDrive/Medical-ML' not in text
        assert not re.search(r'[A-Za-z]:\\(?![nrt"])', text), f'{rel}: absolute Windows path'


def test_inventory_manifest_is_consistent():
    path = ROOT / 'docs/FILE_INVENTORY_SHA256.tsv'
    if not path.exists():
        pytest.skip('inventory generated at release audit time')
    lines = path.read_text(encoding='utf-8').splitlines()
    assert lines[0].startswith('path\tmime\tsize_bytes\tsha256')
    assert len(lines) > 20
