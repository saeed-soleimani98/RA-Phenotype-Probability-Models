# Scientific decisions and amendment policy

This note records the decisions that must **not** be changed to simplify repository construction. Full frozen protocols are in `config/`.

| Decision | Frozen choice | Where enforced |
|:--|:--|:--|
| Outcomes | `NegRFandACCP`, `NoHandJointInvolvement`, `AsymmetricArthritis`, modeled separately | All stage configs and modeling notebooks |
| `OnlyLargeJoints` | EDA only; never primary/sensitivity/final outcome | `RA_EDA.ipynb`, exclusion assertions |
| Confirmatory model | Compact common-core ridge logistic regression, ~9 parameters | `stage3_modeling_decisions.yaml`, `03B*.ipynb` |
| Comparators | Core ordinary logistic; broad ridge/elastic-net secondary/exploratory | Stage 3B/3C |
| Nonlinear algorithms | Exploratory only; cannot promote a model | Stage 3C/4 protocols |
| Validation | Repeated stratified 5-fold × 10-repeat outer CV; 5-fold inner tuning; identical splits per outcome | Stage 3B; saved split assignments |
| Prediction rule | All development performance from OOF predictions; patient average over 10 repeats | Stage 3B/3C/4 |
| Uncertainty | 2,000 stratified patient-level bootstrap resamples | Stage 3B/4 protocols |
| Imbalance | Natural prevalence; no SMOTE, oversampling, undersampling or favorable seed | Stage 3 config, notebook audits |
| Missingness | Fold-contained imputation + indicators; blanks are unknown/not assessed | Stage 2 factory, Stage 4M |
| Reproductive variables | Excluded from all-patient primary models | Stage 2 exclusions |
| `VisitID` | Alignment key only; never a predictor or SHAP feature | All modeling/SHAP notebooks |
| Calibration | Unmodified probabilities first; training-only recalibration sensitivity; no full-data calibration | Stage 3 protocol |
| Thresholds | No fixed 0.50/Youden primary; grid over plausible thresholds | Stage 3 protocol |
| SHAP | Strictly OOF for inference; final-fit SHAP descriptive only; mean absolute ≠ direction; direction predictive not causal | `05_*`, `Complete_SHAP*` |
| Final packaging | Full-cohort refit allowed for model objects; apparent performance forbidden | `stage4g_final_model_protocol.yaml` |
| Reporting | TRIPOD+AI / PROBAST+AI; internal validation only; no clinical deployment claim | All protocols and README |

## Amendment policy

If supplied code appears inconsistent with these principles, the agent must not silently rewrite it. Record the exact file/cell/line, concern and proposed remedy in `PRIVACY_AUDIT_REPORT.md` or a review issue, and ask the owner. Portability edits (path resolution) and privacy redactions (identifier/value removal) are the only changes made during repository construction, and both are documented in `CHANGELOG.md`.
