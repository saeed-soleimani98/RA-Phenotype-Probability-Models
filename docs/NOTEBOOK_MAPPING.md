# Mapping: supplied notebooks → repository locations

All 13 supplied output-free notebooks are preserved. One byte-identical duplicate is archived; all others are executable sources.

| Supplied filename | Repository location | Execution order | Role / note |
|:--|:--|:--|:--|
| `RA_EDA.ipynb` | `notebooks/RA_EDA.ipynb` | 0 | EDA only; `OnlyLargeJoints` appears here only |
| `02_data_cleaning_and_preprocessing.ipynb` | `notebooks/02_data_cleaning_and_preprocessing.ipynb` | 1 | Correction records now loaded from authorized local JSON |
| `03A_sample_size_complexity_feasibility.ipynb` | `notebooks/03A_sample_size_complexity_feasibility.ipynb` | 2 | Feasibility, no model fitting |
| `03B_modeling_validation.ipynb` | `notebooks/03B_modeling_validation.ipynb` | 3 | Confirmatory primary, pipeline v1.1, Colab-compatible |
| `03B_modeling_validation_COLAB_v1_1.ipynb` | `archive/notebooks/03B_modeling_validation_COLAB_v1_1.ipynb` | — | Byte-identical to the above (same SHA-256); retained, not executed |
| `03B_modeling_validation_LOCAL_sklearn18.ipynb` | `notebooks/03B_modeling_validation_LOCAL_sklearn18.ipynb` | 3-alt | Genuine variant: pipeline v1.2, local scikit-learn ≥1.8 API only |
| `03C_exploratory_algorithm_benchmark.ipynb` | `notebooks/03C_exploratory_algorithm_benchmark.ipynb` | 4 | Exploratory benchmark |
| `04_locked_internal_robustness.ipynb` | `notebooks/04_locked_internal_robustness.ipynb` | 5 | Locked robustness |
| `04M_locked_missingness_addendum.ipynb` | `notebooks/04M_locked_missingness_addendum.ipynb` | 6 | Missingness addendum |
| `04M1_tie_preserving_missingness_correction.ipynb` | `notebooks/04M1_tie_preserving_missingness_correction.ipynb` | 7 | Descriptive correction only |
| `04G_final_model_packaging.ipynb` | `notebooks/04G_final_model_packaging.ipynb` | 8 | Final refit/package; no apparent performance |
| `05_directional_oof_shap_check.ipynb` | `notebooks/05_directional_oof_shap_check.ipynb` | 9 | Directional OOF SHAP audit |
| `Complete_SHAP_Analysis_Publication.ipynb` | `notebooks/Complete_SHAP_Analysis_Publication.ipynb` | 10 | Publication SHAP analysis |

### Why the two 03B variants were kept

The `LOCAL_sklearn18` file was compared cell-by-cell against the v1.1 notebook. It differs in version metadata, API construction (`l1_ratio`/`C` only), a hard scikit-learn ≥1.8 requirement, removal of the Colab mount branch, and its pipeline signature. It is a genuine local alternative, not redundant. The `COLAB_v1_1` file is byte-identical to the primary v1.1 notebook (verified by SHA-256 in `docs/ORIGINAL_SOURCE_FILE_MANIFEST.tsv`) and was moved to `archive/` rather than deleted.

### Non-notebook mapping

| Supplied path | Repository location |
|:--|:--|
| `README.md` | `README.md` (rewritten; original retained in `docs/ORIGINAL_PACKAGE_README.md`) |
| `PRIVACY_AND_DATA_GOVERNANCE.md` | `PRIVACY_AND_DATA_GOVERNANCE.md` (verbatim) |
| `FILE_MANIFEST.tsv` | `docs/ORIGINAL_SOURCE_FILE_MANIFEST.tsv` (verbatim, source-package checksums) |
| `.gitignore` | `.gitignore` (replaced by stronger repo-specific rules) |
| `config/*.yaml` | `config/*.yaml` (verbatim) |
| `docs/*.md` | `docs/*.md` (paths generalized; one disclosive note redacted) |
| `environment/*.txt` | `environment/original/*.txt` (verbatim) |
| `scripts/*.py` | `scripts/*.py` (paths generalized; three disclosive decision lines redacted) |
| `src/*.py` | `src/*.py` (verbatim) |
