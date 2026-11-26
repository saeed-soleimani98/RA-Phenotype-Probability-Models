# Rheumatoid arthritis cross-sectional phenotype probability models — analytical code for journal review

> **Repository status: OWNER-APPROVED FOR PUBLIC RELEASE — publication pending push.**
> Repository: `https://github.com/saeed-soleimani98/RA-Phenotype-Probability-Models` · Default branch: `main`.
> The owner authorized public sharing after reviewing the privacy audit. Author/license/DOI/archive metadata remain owner-action placeholders in `CITATION.cff` and `RELEASE_CHECKLIST.md`; no release or archive has been created.

## Purpose and scientific boundary

This repository contains the complete analytical code for a cross-sectional study of three rheumatoid arthritis (RA) phenotype definitions:

| Outcome (modeled separately) | Short description |
|:--|:--|
| `NegRFandACCP` | Negative rheumatoid factor **and** negative anti-CCP |
| `NoHandJointInvolvement` | No hand-joint involvement |
| `AsymmetricArthritis` | Asymmetric arthritis |

`OnlyLargeJoints` appears **only** in exploratory data analysis and is **not** a primary, secondary, sensitivity, or final-modeling outcome.

**Estimand.** The project estimates **cross-sectional phenotype probabilities** from clinical variables collected at a full rheumatology assessment. It is **not** diagnosis, prognosis, causal inference, treatment guidance, a screening tool, or evidence of clinical utility. Performance estimates are **internally validated only**; external validation is required before any clinical use.

**Analysis hierarchy (verbatim scientific decisions):**

```text
PRIMARY (confirmatory)
└─ Stage 3B: leakage-controlled compact common-core ridge logistic models
   ├─ 7 clinical predictors (~9 parameters), L2 tuned in inner CV by log loss
   ├─ repeated stratified 5-fold × 10-repeat outer CV; shared splits across models
   ├─ patient-averaged out-of-fold (OOF) predictions for performance
   └─ 2,000 patient-level bootstrap resamples for uncertainty

SECONDARY / EXPLORATORY
├─ Ordinary logistic regression with the same core (transparent benchmark)
├─ Broad ridge and elastic-net models (all Stage 2 primary-eligible predictors)
└─ Stage 3C: nonlinear algorithm benchmark (post hoc exploratory)

ROBUSTNESS / MISSINGNESS (cannot promote a model to primary)
├─ Stage 4: locked internal robustness, semantic ablations, selector audit, subgroups
├─ Stage 4M: missingness-mechanism addendum (never overrides Stage 3B)
└─ Stage 4M1: descriptive tie-preserving missingness-burden correction

EXPLANATION (two strictly separate layers)
├─ OOF SHAP: signed, patient-averaged across repetitions; VisitID is an alignment key only
└─ Final-fit SHAP: descriptive explanations of full-cohort fitted models; no performance claim

FINAL PACKAGING
└─ Stage 4G: full-cohort refit for research-use-only model objects; apparent performance forbidden
```

## Contents and execution order

The supplied notebooks are preserved output-free. Filenames are kept so that the frozen checkpoint/pipeline signatures still match the executed workflow. `notebooks/00_EXECUTION_ORDER.md` is the in-directory index.

| # | Notebook | Role |
|--:|:--|:--|
| 0 | `notebooks/RA_EDA.ipynb` | EDA, outcome-specific leakage exclusions, derived-data definitions. `OnlyLargeJoints` is inspected here only. |
| 1 | `notebooks/02_data_cleaning_and_preprocessing.ipynb` | Verified cleaning, investigator-agreed corrections (loaded from an authorized local file), railed/constant handling, leakage-controlled predictor manifests. |
| 2 | `notebooks/03A_sample_size_complexity_feasibility.ipynb` | Riley-style complexity feasibility; explains why the compact core is confirmatory. No model is fitted. |
| 3 | `notebooks/03B_modeling_validation.ipynb` | **Primary analysis.** Repeated nested CV for the three outcomes and four models; patient-averaged OOF estimates, calibration, bootstrap intervals, OOF SHAP inputs. |
| 3-alt | `notebooks/03B_modeling_validation_LOCAL_sklearn18.ipynb` | Local variant (pipeline v1.2) using only the scikit-learn ≥1.8 API. Use **instead of**, not after, notebook 3 when running locally with scikit-learn 1.8–1.9. |
| 4 | `notebooks/03C_exploratory_algorithm_benchmark.ipynb` | Post hoc exploratory algorithm benchmark reusing saved Stage 3B splits. |
| 5 | `notebooks/04_locked_internal_robustness.ipynb` | Locked robustness: selector audit, domain ablations, calibration bands, subgroup evaluation only. |
| 6 | `notebooks/04M_locked_missingness_addendum.ipynb` | Locked missingness-mechanism sensitivity analyses; no new model families. |
| 7 | `notebooks/04M1_tie_preserving_missingness_correction.ipynb` | Descriptive correction of rank-based missingness-burden ties. No refitting. |
| 8 | `notebooks/04G_final_model_packaging.ipynb` | Full-cohort final refits for research-use-only packages; no apparent performance. |
| 9 | `notebooks/05_directional_oof_shap_check.ipynb` | Directional OOF SHAP audit and HTML report. |
| 10 | `notebooks/Complete_SHAP_Analysis_Publication.ipynb` | Publication SHAP tables/figures from OOF and final-fit explanations, kept separate. |

`archive/notebooks/03B_modeling_validation_COLAB_v1_1.ipynb` is a **byte-identical copy** of notebook 3 (same SHA-256 in the source manifest). It is retained under `archive/` rather than deleted, and is not part of the execution order. See `docs/NOTEBOOK_MAPPING.md` for the complete original-name → repository-location mapping.

Supporting directories:

```text
src/          reusable preprocessing and final-model components
scripts/      report, figure, SHAP-notebook and manuscript utilities
config/       frozen analysis/robustness protocols + portable path notes
docs/         original run instructions/audits + reviewer and science guides
environment/  consolidated requirements.txt + original/ requirements files
tests/        static, schema-level and data-free tests
tools/        privacy audit / inventory utilities
```

## What reviewers can and cannot do

**Can inspect without data:** every notebook cell, all frozen protocols, the model hierarchy, leakage exclusions, validation logic, SHAP rules, audits, and the static test suite. Run:

```bash
python -m pip install -r environment/requirements.txt
python -m pytest -q tests
```

The tests require **no clinical data** and do not fetch anything. They validate notebook hygiene (valid JSON, zero outputs, zero execution counts), Python compilation, YAML syntax, filename/content privacy rules, path portability, and a few tiny programmatic array interfaces.

**Cannot do without authorization:** execute data-dependent cells, recompute OOF metrics, reproduce bootstrap intervals, inspect patient-level SHAP values, or reload model packages. Participant-level data and derived patient-level artifacts are deliberately absent. Numerical reproduction requires separately authorized access to the source cohort. See `docs/DATA_AVAILABILITY.md` and `docs/CODE_AVAILABILITY.md`.

## Authorized-user configuration

1. Copy `.env.example` to `.env` and set `RA_PROJECT_DIR`, `RA_DATA_PATH`, `RA_OUTPUT_DIR`, `RA_ARTIFACT_DIR`, and `RA_CORRECTIONS_PATH` to **authorized local** locations outside version control.
2. Load the variables into your shell or kernel (`set -a; source .env; set +a`).
3. Follow `docs/REVIEWER_GUIDE.md` and the original stage-specific run instructions under `docs/`.
4. Never place restricted files inside this repository directory.

`config/corrections_template.json` documents the schema of the withheld correction specification. It contains placeholders only — no identifiers, values, frequencies, or patient examples.

## Reproducibility scope

Internally validated **patient-averaged OOF** performance is the evidence base. Full-cohort final refits in Stage 4G are descriptive model objects only; **no apparent full-cohort performance is calculated or reported**. OOF SHAP and final-fit SHAP outputs are separate artifacts. Random seeds, software versions, and expected artifact families are recorded in `REPRODUCIBILITY.md`. Cross-platform bitwise reproducibility is **not claimed**.

## Privacy and ethics

No participant-level data, identifiers, row-level predictions, fold assignments, bootstrap rows, patient-level SHAP values, trained model binaries, notebook outputs, or credentials are committed. Machine-specific paths and three disclosive items found in the supplied materials were sanitized before the first commit; every change is recorded in `PRIVACY_AUDIT_REPORT.md`. Anonymization is **not** claimed to make the dataset safe to share: the owner has decided not to share data for ethical and governance reasons.

## Citation

The repository has **no author names, affiliations, ethics identifiers, funders, DOI, journal article, or archive identifier yet**. These are explicit owner-action placeholders in `CITATION.cff` and `docs/CODE_AVAILABILITY.md`. When known, replace `[REPOSITORY URL]`, `[DOI OR RELEASE IDENTIFIER]`, `[COMMIT HASH]`, `[AUTHORS]`, `[YEAR]`, and `[TITLE]` consistently. Record the exact reviewed commit hash in the manuscript and in any immutable archive.

## Owner decisions still required

Repository name/account, software license, public/private status, issues/discussions/forks/third-party integrations, author and contact details, ethics/funder/institution metadata, DOI/Zenodo/OSF archive, and the final versioned release. Code without a license is **not** openly reusable; the owner must choose one. See `RELEASE_CHECKLIST.md`.
