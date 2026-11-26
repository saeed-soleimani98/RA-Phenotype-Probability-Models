# Stage 4G — Final Model Fitting and Packaging

## Purpose

Stage 4G fits the frozen model candidates to all 820 development patients and creates portable research-use model packages. It does not calculate apparent full-cohort performance. All performance evidence remains the repeated nested OOF evidence from Stages 3B–4.

## Copy to `the authorized RA_PROJECT_DIR`

- `04G_final_model_packaging.ipynb`
- `stage4g_final_model_protocol.yaml`
- `ra_final_model_components.py`
- `requirements-stage4.txt`

Retain the existing completed directories:

- `derived_data/`
- `modeling_results/`
- `modeling_results_stage3c/`

## Full run

```cmd
conda activate ml
cd /d the authorized RA_PROJECT_DIR
set RA_PROJECT_DIR=the authorized RA_PROJECT_DIR
set RA_STAGE4G_QUICK_TEST=
set RA_STAGE4G_FORCE_RECOMPUTE=
jupyter lab
```

Open `04G_final_model_packaging.ipynb`, select the same environment used for Stages 3C–4, and run all cells.

Full mode uses repeated stratified 5-fold CV × 10 repeats for final hyperparameter selection. Ridge uses the frozen grids and a one-standard-error rule favoring stronger regularization. XGBoost evaluates 50 deterministic candidates from the locked Stage 3C space and applies the frozen one-standard-error simplicity rule.

The XGBoost searches are the longest operations. Do not interrupt an individual XGBoost search. Completed model packages are automatically reused if the signed run definition is unchanged.

## Models packaged

Primary:

- core ridge for `NegRFandACCP`
- core ridge for `NoHandJointInvolvement`
- core ridge for `AsymmetricArthritis`

Secondary:

- broad ridge for all three outcomes

Exploratory challengers:

- XGBoost for `NoHandJointInvolvement`
- XGBoost for `AsymmetricArthritis`

`OnlyLargeJoints` is excluded.

## Outputs

Full outputs are isolated under:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4g
```

The portable model package is:

```text
modeling_results_stage4g\final_model_package
```

The final report is:

```text
modeling_results_stage4g\report\Stage4G_final_model_packaging_report.html
```

A flat directory with uniquely named files for independent audit is created at:

```text
modeling_results_stage4g\audit_upload
```

## Required verification

Confirm that:

1. `stage4g_run_summary.json` reports `mode: full`;
2. eight models were packaged;
3. all 30 rows in `tables\stage4g_validation_audit.csv` are `PASS`;
4. all rows in `reload_prediction_validation.csv` and `cli_prediction_validation.csv` pass;
5. no apparent full-data performance table exists;
6. every pipeline, model card, predictor dictionary, example, and checksum is present.

## Optional software-only quick test

```cmd
set RA_STAGE4G_QUICK_TEST=1
```

Quick mode writes to `modeling_results_stage4g_quick`, uses reduced CV/search settings, and is software validation only. Clear the variable before the full run:

```cmd
set RA_STAGE4G_QUICK_TEST=
```

## Files to upload for independent audit

Upload:

- `Stage4G_final_model_packaging_report.html`
- `tables\stage4g_validation_audit.csv`
- `tables\final_model_registry.csv`
- `tables\all_final_tuning_candidates.csv`
- `tables\reload_prediction_validation.csv`
- `tables\cli_prediction_validation.csv`
- `tables\prior_oof_performance_reference.csv`
- `tables\artifact_registry.csv`
- `stage4g_run_summary.json`
- every uniquely named `__metadata.json`, `__MODEL_CARD.md`, and `__pipeline.joblib` file from `audit_upload`

Keep the entire `final_model_package` directory unchanged for future external validation.
