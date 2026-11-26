# Notebook execution order

Run in this order only with separately authorized data. `03B_LOCAL_sklearn18` is an **alternative** to `03B_modeling_validation`, not an additional step. The archived Colab copy is byte-identical to `03B_modeling_validation` and is not executed.

| Order | File | Purpose | Prerequisite outputs |
|--:|:--|:--|:--|
| 0 | `RA_EDA.ipynb` | Exploratory analysis and outcome-specific exclusion definitions; `OnlyLargeJoints` is EDA-only. | Restricted source CSV (`RA_DATA_PATH`) |
| 1 | `02_data_cleaning_and_preprocessing.ipynb` | Verified corrections and leakage-controlled derived data/manifests. | Step 0; authorized correction JSON (`RA_CORRECTIONS_PATH`) |
| 2 | `03A_sample_size_complexity_feasibility.ipynb` | Complexity/Riley feasibility; no model fitting. | Step 1 derived data |
| 3 | `03B_modeling_validation.ipynb` | **Confirmatory primary** repeated nested CV and OOF evaluation. | Steps 1–2; frozen `config/stage3_modeling_decisions.yaml` |
| 3-alt | `03B_modeling_validation_LOCAL_sklearn18.ipynb` | Same analysis, scikit-learn 1.8+ local API (pipeline v1.2). Use instead of step 3. | Same as step 3 |
| 4 | `03C_exploratory_algorithm_benchmark.ipynb` | Post hoc exploratory algorithm benchmark. | Stage 3B saved splits and OOF predictions |
| 5 | `04_locked_internal_robustness.ipynb` | Locked robustness and domain-removal analyses. | Stage 3B/3C checkpoints |
| 6 | `04M_locked_missingness_addendum.ipynb` | Missingness-mechanism sensitivity analyses. | Stage 3B/3C/4 products |
| 7 | `04M1_tie_preserving_missingness_correction.ipynb` | Descriptive tie correction; no refitting. | Step 6 descriptive tables |
| 8 | `04G_final_model_packaging.ipynb` | Full-cohort refit/packages; no apparent performance. | Stage 3B/3C/4 products |
| 9 | `05_directional_oof_shap_check.ipynb` | Directional OOF SHAP audit. | Patient-averaged OOF predictions (authorized local) |
| 10 | `Complete_SHAP_Analysis_Publication.ipynb` | Publication SHAP summaries; OOF and final-fit kept separate. | Stage 4G package + OOF SHAP inputs |

Never use software-only quick-test switches for scientific results.
