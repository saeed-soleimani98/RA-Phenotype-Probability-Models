# Stage 3C — local run instructions

## Scientific status

This notebook is a **post hoc exploratory algorithm benchmark**. Stage 3B remains the frozen prespecified primary analysis. Stage 3C reads the Stage 3B split assignments and reference predictions but writes only to `modeling_results_stage3c/`.

## Required project layout

Set `RA_PROJECT_DIR` to the directory containing the prior-stage products expected by the notebook:

- `cleaned_data/cleaned_master_data.csv`
- `derived_data/`
- `preprocessing_outputs/tables/stage2_validation_audit.csv`
- `modeling_feasibility/tables/stage3a_validation_audit.csv`
- `modeling_results/tables/saved_outer_split_assignments.csv`
- `modeling_results/tables/patient_averaged_oof_predictions.csv`
- `modeling_results/tables/stage3b_validation_audit.csv`
- `stage3_modeling_decisions.yaml` (the notebook also checks several documented fallback locations)

If your existing project root is `stage2_outputs`, point `RA_PROJECT_DIR` there.

## 1. Create an isolated environment

### Windows PowerShell

```powershell
cd the authorized RA_PROJECT_DIR
py -3.13 -m venv .venv-stage3c
.\.venv-stage3c\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-stage3c.txt
python -m ipykernel install --user --name ra-stage3c --display-name "RA Stage 3C"
$env:RA_PROJECT_DIR = "the authorized RA_PROJECT_DIR\stage2_outputs"
jupyter lab
```

### macOS/Linux

```bash
cd /path/to/ra_analysis
python3 -m venv .venv-stage3c
source .venv-stage3c/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-stage3c.txt
python -m ipykernel install --user --name ra-stage3c --display-name "RA Stage 3C"
export RA_PROJECT_DIR="/path/to/project/stage2_outputs"
jupyter lab
```

Open `03C_exploratory_algorithm_benchmark.ipynb`, choose the **RA Stage 3C** kernel, and run all cells. The default is the full scientific run: 5-fold × 10-repeat saved outer validation, 5-fold inner tuning, and 2,000 patient-level bootstrap replicates.

## 2. Optional software-only quick validation

Quick mode is only a pipeline test and must not be reported as a scientific result.

PowerShell:

```powershell
$env:RA_STAGE3C_QUICK_TEST = "1"
```

macOS/Linux:

```bash
export RA_STAGE3C_QUICK_TEST=1
```

Unset the variable before the full run. To invalidate matching signed checkpoints and recompute, set `RA_STAGE3C_FORCE_RECOMPUTE=1` for that run. XGBoost defaults to CPU; a supported alternative can be requested with `RA_STAGE3C_XGB_DEVICE`.

## 3. Outputs and verification

Outputs are isolated under `modeling_results_stage3c/`, including tables, figures, signed checkpoints, report assets, run metadata, and the artifact registry. The final notebook cell reconstructs the report from signed checkpoints and exports a self-contained HTML file.

Before interpreting results, confirm:

1. the run summary says `mode: full`;
2. all 24 rows of `tables/stage3c_validation_audit.csv` are `PASS`;
3. the report identifies Stage 3C as exploratory and Stage 3B as primary;
4. no Stage 3B fingerprint/immutability check failed;
5. all three outcomes and all nine Stage 3C model families completed.

Do not mix quick and full checkpoints. Checkpoint signatures include the mode and pipeline version, but a separate clean output directory is preferable for the final scientific run.
