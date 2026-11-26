"""Static checks that frozen scientific decisions remain visible in the code."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def notebook_text(name: str) -> str:
    nb = json.loads((ROOT / 'notebooks' / name).read_text(encoding='utf-8'))
    return '\n'.join(''.join(c.get('source', [])) for c in nb['cells'])


def test_three_primary_outcomes_in_frozen_protocol():
    cfg = yaml.safe_load((ROOT / 'config/stage3_modeling_decisions.yaml').read_text())
    assert cfg['outcomes'] == ['NegRFandACCP', 'NoHandJointInvolvement', 'AsymmetricArthritis']


def test_only_large_joints_excluded_from_all_frozen_protocols():
    for path in (ROOT / 'config').glob('*.yaml'):
        cfg = yaml.safe_load(path.read_text())
        assert 'OnlyLargeJoints' not in cfg.get('outcomes', [])
        if 'excluded_outcomes' in cfg:
            assert 'OnlyLargeJoints' in cfg['excluded_outcomes']


def test_stage2_corrections_are_externalized():
    text = notebook_text('02_data_cleaning_and_preprocessing.ipynb')
    assert '_load_authorized_corrections()' in text
    assert 'RA_CORRECTIONS_PATH' in text
    for ident in ('2127', '24594', '10550', '10709', '4.070393341399587'):
        assert ident not in text, f'participant-level value {ident} still present'


def test_visitid_is_alignment_key_not_predictor():
    modeling = '\n'.join(notebook_text(name) for name in (
        '03B_modeling_validation.ipynb', '03C_exploratory_algorithm_benchmark.ipynb',
        '04_locked_internal_robustness.ipynb', '04M_locked_missingness_addendum.ipynb'))
    assert "'VisitID' in predictors" in modeling
    shap = notebook_text('Complete_SHAP_Analysis_Publication.ipynb')
    assert 'VisitID' in shap and 'prohibited' in shap.lower()


def test_no_forbidden_resampling_in_frozen_protocol():
    cfg = yaml.safe_load((ROOT / 'config/stage3_modeling_decisions.yaml').read_text())
    banned = {str(x).lower() for x in cfg['class_imbalance']['excluded']}
    assert 'smote' in banned and 'undersampling' in banned


def test_oof_and_final_fit_are_separated():
    cfg = yaml.safe_load((ROOT / 'config/stage4g_final_model_protocol.yaml').read_text())
    assert 'Previously reported repeated nested OOF estimates only' in cfg['scientific_hierarchy']['performance_evidence']
    assert any('apparent' in str(x).lower() and 'performance' in str(x).lower() for x in cfg['prohibitions'])


def test_shap_direction_rules_are_documented():
    text = (ROOT / 'REPRODUCIBILITY.md').read_text(encoding='utf-8')
    for phrase in ('mean(|SHAP|)', 'provide direction', 'predictive, not causal'):
        assert phrase in text


def test_missingness_blank_policy_is_documented():
    text = (ROOT / 'CODEBOOK_TEMPLATE.md').read_text(encoding='utf-8')
    assert 'unknown / not assessed' in text
    assert 'never coerced to 0' in text
