"""Notebook hygiene tests — no clinical data required."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted(ROOT.glob('notebooks/*.ipynb')) + sorted(ROOT.glob('archive/notebooks/*.ipynb'))


def test_all_13_supplied_notebooks_present():
    assert len(NOTEBOOKS) == 13, f'expected 13 preserved notebooks, found {len(NOTEBOOKS)}'


@pytest.mark.parametrize('path', NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_is_valid_json(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data.get('nbformat') in (4, 5)
    assert isinstance(data.get('cells'), list) and data['cells']


@pytest.mark.parametrize('path', NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_has_no_outputs_or_execution_counts(path: Path):
    nb = json.loads(path.read_text(encoding='utf-8'))
    for i, cell in enumerate(nb['cells']):
        assert not cell.get('outputs'), f'{path.name}: outputs in cell {i}'
        assert cell.get('execution_count') is None, f'{path.name}: execution_count in cell {i}'


@pytest.mark.parametrize('path', NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_has_no_embedded_binary_payloads(path: Path):
    text = path.read_text(encoding='utf-8')
    assert not re.search(r'data:image/[A-Za-z+]+;base64,[A-Za-z0-9+/]{100,}', text)
    # Long base64-like runs would indicate embedded outputs or blobs.
    for match in re.finditer(r'[A-Za-z0-9+/]{240,}={0,2}', text):
        try:
            base64.b64decode(match.group(0), validate=True)
        except Exception:
            continue
        pytest.fail(f'{path.name}: embedded base64 payload')


@pytest.mark.parametrize('path', NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_has_no_absolute_private_paths(path: Path):
    nb = json.loads(path.read_text(encoding='utf-8'))
    text = '\n'.join(''.join(c.get('source', [])) for c in nb['cells'])
    assert not re.search(r'[A-Za-z]:\\(?![nrt"])', text), f'{path.name}: Windows absolute path'
    assert '/' + 'home/user' not in text and '/content/drive/MyDrive' not in text
