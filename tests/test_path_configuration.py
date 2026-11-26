"""Path-helper tests. No clinical data or downloads are used."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
ra_paths = importlib.import_module('ra_paths')


def test_missing_configuration_raises_clear_error(monkeypatch):
    for name in ('RA_PROJECT_DIR', 'RA_DATA_PATH', 'RA_OUTPUT_DIR', 'RA_ARTIFACT_DIR', 'RA_CORRECTIONS_PATH'):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ra_paths.MissingConfiguration, match='RA_PROJECT_DIR'):
        ra_paths.project_dir(required=True)
    with pytest.raises(ra_paths.MissingConfiguration, match='RA_DATA_PATH'):
        ra_paths.data_path(required=True)
    with pytest.raises(ra_paths.MissingConfiguration, match='RA_ARTIFACT_DIR'):
        ra_paths.artifact_dir(required=True)
    with pytest.raises(ra_paths.MissingConfiguration, match='RA_CORRECTIONS_PATH'):
        ra_paths.correction_spec_path(required=True)


def test_environment_paths_are_used(monkeypatch, tmp_path):
    monkeypatch.setenv('RA_PROJECT_DIR', str(tmp_path / 'project'))
    monkeypatch.setenv('RA_DATA_PATH', str(tmp_path / 'source.csv'))
    monkeypatch.setenv('RA_OUTPUT_DIR', str(tmp_path / 'out'))
    monkeypatch.setenv('RA_CORRECTIONS_PATH', str(tmp_path / 'corrections.json'))
    assert ra_paths.project_dir(required=True) == tmp_path / 'project'
    assert ra_paths.data_path(required=True) == tmp_path / 'source.csv'
    assert ra_paths.output_dir() == tmp_path / 'out'
    assert ra_paths.correction_spec_path(required=True) == tmp_path / 'corrections.json'


def test_unexpanded_placeholder_is_rejected(monkeypatch):
    monkeypatch.setenv('RA_DATA_PATH', '/path/to/authorized/restricted_source.csv')
    with pytest.raises(ra_paths.MissingConfiguration, match='unexpanded placeholder'):
        ra_paths.data_path()


def test_preprocessor_interface_with_tiny_programmatic_frame():
    pytest.importorskip('sklearn')
    pandas = pytest.importorskip('pandas')
    factory = importlib.import_module('preprocessing_factory')
    frame = pandas.DataFrame({
        'num': [1.0, 2.0, 3.0, 4.0],
        'bin': [0.0, 1.0, 0.0, None],
        'cat': ['a', 'b', 'a', 'b'],
    })
    groups = factory.load_column_groups  # interface exists; no patient-like fixture used
    assert callable(groups)
    transformer = factory.make_preprocessor({'numeric': ['num'], 'binary': ['bin'], 'categorical': ['cat']})
    transformed = transformer.fit_transform(frame)
    assert transformed.shape[0] == 4
    assert transformed.shape[1] >= 3
