# Stage 4 Missingness Addendum — local execution

## Files to place in `the authorized RA_PROJECT_DIR`

- `04M_locked_missingness_addendum.ipynb`
- `stage4_missingness_addendum_protocol.yaml`
- `requirements-stage4.txt`

Keep the existing project directories:

- `derived_data/`
- `modeling_results/`
- `modeling_results_stage3c/`

The notebook accepts either `modeling_results_stage3c/tables/` or `modeling_results_stage3c/tables-3c/`.

## Full scientific run

In Anaconda Prompt:

```cmd
conda activate ml
cd /d the authorized RA_PROJECT_DIR
set RA_PROJECT_DIR=the authorized RA_PROJECT_DIR
set RA_STAGE4M_QUICK_TEST=
set RA_STAGE4M_FORCE_RECOMPUTE=
jupyter lab
```

Open `04M_locked_missingness_addendum.ipynb`, select the same `ml` kernel used for Stages 3C–4, and run all cells.

Do **not** set `RA_STAGE4M_QUICK_TEST` for the scientific run. Full mode uses:

- exact Stage 3B 5-fold × 10-repeat outer assignments;
- 5-fold inner tuning;
- 2,000 paired patient bootstrap resamples;
- the frozen 21-value ridge grid;
- the frozen 50-candidate XGBoost search for the NoHand no-flags sensitivity;
- natural prevalence without class weighting or resampling.

## Resume behavior

One signed checkpoint is saved after every outer-fold fit under:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4_missingness\checkpoints
```

If interrupted, rerun all cells. Compatible completed fits load automatically. Do not set `RA_STAGE4M_FORCE_RECOMPUTE=1` unless you intentionally want to invalidate and repeat all fits.

## Outputs

All new outputs are isolated under:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4_missingness
```

The notebook does not overwrite Stages 3B, 3C, or 4. Its final cell creates:

```text
modeling_results_stage4_missingness\report\Stage4_missingness_addendum_report.html
```

Before interpretation, confirm:

1. `stage4_missingness_run_summary.json` reports `mode: full`;
2. all 28 rows in `tables/stage4_missingness_validation_audit.csv` are `PASS`;
3. every patient has 10 OOF repetitions in `tables/missingness_sensitivity_patient_averaged_predictions.csv`;
4. there are 500 completed outer fits in `tables/missingness_sensitivity_fit_diagnostics.csv`.

## Optional software-only quick test

```cmd
set RA_STAGE4M_QUICK_TEST=1
```

Quick mode uses one repeat, three outer folds, two inner folds, 100 bootstraps, three ridge candidates, and four XGBoost candidates. It validates software only and must not support scientific interpretation.

Clear it before the full run:

```cmd
set RA_STAGE4M_QUICK_TEST=
```

## What to return for independent review

Upload the full HTML report plus these CSVs from `modeling_results_stage4_missingness\tables`:

- `stage4_missingness_validation_audit.csv`
- `missingness_sensitivity_fit_diagnostics.csv`
- `missingness_sensitivity_all_repeated_oof_predictions.csv`
- `missingness_sensitivity_patient_averaged_predictions.csv`
- `missingness_sensitivity_performance.csv`
- `missingness_sensitivity_bootstrap_ci.csv`
- `missingness_sensitivity_paired_vs_original.csv`
- `predictor_missingness_by_outcome_status.csv`
- `outcome_prevalence_by_missingness_burden.csv`
- `common_exact_missingness_patterns.csv`
- `near_complete_predictor_selection_frequency.csv`
- `site_calendar_metadata_availability.csv`
- `artifact_registry.csv`
