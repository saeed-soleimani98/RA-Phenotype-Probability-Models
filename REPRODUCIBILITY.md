# Reproducibility scope and limitations

## Validation layers

| Layer | What it is | What it supports | What it does not support |
|:--|:--|:--|:--|
| Patient-averaged OOF | Repeated 5-fold × 10-repeat nested CV; each patient's 10 OOF probabilities averaged; 2,000 stratified patient bootstraps | Internally validated performance estimates and paired model comparisons | Clinical utility, external validity, causal interpretation |
| Stability evidence | Outer-fold and repetition distributions | Sensitivity of estimates to split variation | Independent observations; 50 correlated folds are not 50 independent samples |
| Final full-cohort refit (Stage 4G) | Models fitted to all 820 development patients for research-use-only packaging | Reloadable model objects, coefficients, predictor dictionary | Apparent performance; no full-data performance is calculated or reported |
| OOF SHAP | Signed OOF explanations averaged per patient across repetitions, linked to raw predictors with `VisitID` used **only** for alignment | Predictive direction/magnitude/rank stability audits | Causal effects; direction under correlated predictors may shift |
| Final-fit SHAP | Explanations of full-cohort fitted models | Descriptive explanation of packaged models | Any performance or generalization claim |

`mean(|SHAP|)` is a magnitude measure only; it does **not** provide direction. Mean signed SHAP is retained for audit but is not used as an importance measure because opposite patient-level contributions can cancel. SHAP direction is predictive, not causal, and may change among correlated predictors.

## Seeds and versions

The frozen protocols record the master seed (`20261020` in Stage 4G), CV structure, tuning objectives and grids. The executed environment used Python 3.13 for Stages 3C/4 with scikit-learn 1.8–1.9; Stage 3B v1.1 supports scikit-learn 1.6–1.9, while the `LOCAL_sklearn18` variant requires ≥1.8. Original requirements files are preserved in `environment/original/`; `environment/requirements.txt` is a conservative merged specification.

Software versions are printed inside notebooks at runtime and recorded in signed checkpoints on authorized machines. **Cross-platform bitwise reproducibility is not claimed**: BLAS/CPU differences and library versions can perturb near-tied ranks and bootstrap endpoints. The supplied independent audit documents small floating-point/tie-sensitive discrepancies below 0.0001 in Stage 3C comparisons.

## Expected artifacts (authorized local only)

Running the notebooks with authorized data generates, outside version control, derived data, saved split assignments, patient-averaged OOF predictions, performance/bootstrap/paired-comparison tables, calibration figures, signed checkpoints, final model packages, and OOF/final-fit SHAP outputs. None are committed here. See `config/PATH_CONFIGURATION.md` for environment variables.

## Integrity principles preserved

Outcome-specific leakage exclusions; VisitID never a predictor; reproductive variables excluded from all-patient primary models; training-fold-only preprocessing/tuning; patient-level repeated nested CV; patient-averaged OOF evaluation; patient-level bootstrap inference; separation of OOF evaluation from final refits; missingness/domain-removal robustness; no SMOTE, oversampling, undersampling, favorable seed selection, global feature selection, or apparent full-cohort performance. Blank binary and comorbidity values remain **unknown/not assessed**, not absent.
