# Reviewer guide (data-free inspection)

This repository is intended for **inspection of the complete analytical workflow**, not for numerical reproduction without authorized data. No clinical data or patient-level derivatives are included.

## Start here

1. `README.md` — outcomes, analysis hierarchy, execution order, scope limits.
2. `config/stage3_modeling_decisions.yaml` — frozen confirmatory protocol.
3. `config/stage4_robustness_protocol.yaml`, `stage4_missingness_addendum_protocol.yaml`, `stage4_missingness_tie_correction_protocol.yaml`, `stage4g_final_model_protocol.yaml` — frozen post hoc and final-fit protocols.
4. `docs/NOTEBOOK_MAPPING.md` — all 13 supplied notebooks and their roles.
5. `docs/Stage3B_full_scientific_review.md`, `docs/Stage3C_independent_complete_audit.md`, `docs/Stage4_full_scientific_review.md`, `docs/Stage4M_full_scientific_review.md`, `docs/Stage4G_full_audit_and_final_model_review.md` — scientific audits.

## Primary notebooks to inspect

| Question | Notebook / section |
|:--|:--|
| How were outcomes and leakage exclusions defined? | `RA_EDA.ipynb`, `02_data_cleaning_and_preprocessing.ipynb` |
| Why is the compact core confirmatory? | `03A_sample_size_complexity_feasibility.ipynb`, `docs/stage3a_key_findings.md` |
| How were OOF estimates produced? | `03B_modeling_validation.ipynb` (and its local variant) |
| What exploratory comparisons were run? | `03C_exploratory_algorithm_benchmark.ipynb` |
| Which robustness and missingness analyses cannot promote a model? | `04_locked_internal_robustness.ipynb`, `04M_locked_missingness_addendum.ipynb`, `04M1_tie_preserving_missingness_correction.ipynb` |
| How were final models packaged without apparent performance? | `04G_final_model_packaging.ipynb` |
| How were SHAP directions audited? | `05_directional_oof_shap_check.ipynb`, `Complete_SHAP_Analysis_Publication.ipynb` |

## Checks possible without data

```bash
python -m pip install -r environment/requirements.txt
python -m pytest -q tests
```

These checks confirm:

* every notebook is valid JSON with **zero outputs and zero execution counts**;
* all Python files compile;
* all YAML files parse;
* tracked filenames/content avoid prohibited data/model formats and disclosure patterns;
* no absolute private paths, emails, signed URLs or credential-like strings remain;
* path helpers raise clear errors when authorized configuration is absent;
* small programmatic arrays exercise preprocessing interfaces without resembling patients.

## Checks that require authorized data

Do **not** attempt these from the public repository: execute any modeling cell, recompute OOF/bootstrap metrics, obtain fold assignments or patient-level SHAP values, reload final model packages, or evaluate apparent performance. These operations need the restricted cohort and locally generated artifacts under `RA_OUTPUT_DIR` / `RA_ARTIFACT_DIR`.

## Reporting concerns

Open an issue **only if the owner enables issues**. Otherwise contact the owner through the channel specified in `DATA_AVAILABILITY.md` once that contact has been supplied. Cite the exact file and cell or line; do not request participant-level material.
