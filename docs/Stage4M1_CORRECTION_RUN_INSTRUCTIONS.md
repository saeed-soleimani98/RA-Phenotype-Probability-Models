# Stage 4M.1 Missingness-Tie Correction — Run Instructions

## Purpose

This is a reporting correction only. It performs no model fitting or tuning. It replaces invalid row-order-dependent missingness tertiles with tie-preserving groups and reevaluates saved OOF predictions within those groups.

## Copy to `the authorized RA_PROJECT_DIR`

- `04M1_tie_preserving_missingness_correction.ipynb`
- `stage4_missingness_tie_correction_protocol.yaml`

Retain the existing completed directories:

- `derived_data/`
- `modeling_results/`
- `modeling_results_stage3c/`
- `modeling_results_stage4/`
- `modeling_results_stage4_missingness/`

## Run

```cmd
conda activate ml
cd /d the authorized RA_PROJECT_DIR
set RA_PROJECT_DIR=the authorized RA_PROJECT_DIR
jupyter lab
```

Open `04M1_tie_preserving_missingness_correction.ipynb` and run all cells.

No quick/full switch is required because no model is refitted. The notebook evaluates the already saved full patient-averaged OOF predictions and uses 2,000 patient-bootstrap resamples for evaluable corrected groups.

## Outputs

Outputs are isolated under:

```text
the authorized RA_PROJECT_DIR\modeling_results_stage4_missingness_correction
```

The final report is:

```text
modeling_results_stage4_missingness_correction\report\Stage4_missingness_tie_correction_report.html
```

Important tables:

- `corrected_patient_missingness_groups.csv`
- `corrected_outcome_prevalence_by_missingness_group.csv`
- `corrected_stage4_locked_model_missingness_group_performance.csv`
- `corrected_stage4m_sensitivity_missingness_group_performance.csv`
- `missingness_tie_correction_audit.csv`
- `artifact_registry.csv`

## Verification

Confirm all 20 audit rows are `PASS`. The corrected prevalence table should contain:

- `NegRFandACCP`: 104/374 complete, 51/257 >0–5%, 9/189 >5%.
- `NoHandJointInvolvement`: 78/274 complete, 95/347 >0–5%, 18/199 >5%.
- `AsymmetricArthritis`: 48/274 complete, 70/347 >0–5%, 72/199 >5%.

## Files to return

Upload:

1. `Stage4_missingness_tie_correction_report.html`
2. all six CSV files listed above
3. `correction_note.json`
4. `correction_run_summary.json`

After verification, no further internal model development is planned. The next phase is manuscript assembly.
