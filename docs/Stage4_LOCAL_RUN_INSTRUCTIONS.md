# Stage 4 — local execution

## Files to place in `the authorized RA_PROJECT_DIR`

- `04_locked_internal_robustness.ipynb`
- `stage4_robustness_protocol.yaml`
- `requirements-stage4.txt`

The project must retain the existing `derived_data/`, `modeling_results/`, and `modeling_results_stage3c/` directories. The notebook accepts either `modeling_results_stage3c/tables/` or the existing `modeling_results_stage3c/tables-3c/` name.

## Run

In Anaconda Prompt:

```cmd
conda activate ml
cd /d the authorized RA_PROJECT_DIR
set RA_PROJECT_DIR=the authorized RA_PROJECT_DIR
jupyter lab
```

Open `04_locked_internal_robustness.ipynb`, select the same `ml` kernel used for Stage 3C, save the notebook in `the authorized RA_PROJECT_DIR`, and run all cells.

Do **not** set `RA_STAGE4_QUICK_TEST` for the scientific run. Full mode uses the 5-fold × 10-repeat Stage 3B splits, 5-fold inner tuning, 2,000 patient bootstraps, 500 calibration-band bootstraps, and per-fold signed checkpoints.

## Resume behavior

A signed checkpoint is saved after every completed ablation outer fold under:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4\checkpoints
```

If execution is interrupted, rerun all cells. Compatible completed folds load automatically. Do not set `RA_STAGE4_FORCE_RECOMPUTE` unless intentional invalidation is required.

The fully nested family-selector analysis requires no refitting; it uses saved Stage 3C inner scores and untouched outer-test predictions.

## Outputs

Stage 4 writes only to:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4
```

It does not overwrite Stage 3B or Stage 3C. Figures are displayed in the notebook and saved as 400-DPI PNG plus vector SVG. The final cell reruns from signed checkpoints and creates:

```text
modeling_results_stage4\report\Stage4_locked_internal_robustness_report.html
```

Before interpretation, verify that `stage4_run_summary.json` says `mode: full` and all 28 rows in `tables/stage4_validation_audit.csv` are `PASS`.

## Optional software-only quick test

```cmd
set RA_STAGE4_QUICK_TEST=1
```

Quick mode is only a software test. Open a new Anaconda Prompt or run `set RA_STAGE4_QUICK_TEST=` before the full scientific run.
