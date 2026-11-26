# Code availability

## What is available

The repository contains the complete analytical source code:

* 13 output-free notebooks covering EDA, cleaning, feasibility, primary repeated nested validation, exploratory benchmarking, locked robustness, missingness analyses, a descriptive tie correction, final model packaging, and OOF/final-fit SHAP procedures;
* reusable preprocessing and model components in `src/`;
* report, figure, manuscript and SHAP utilities in `scripts/`;
* frozen modeling/robustness/missingness/final-model protocols in `config/`;
* original run instructions and independent scientific audits in `docs/`;
* data-free static and schema-level tests in `tests/`, plus CI and pre-commit configuration.

## What is not available

Participant-level data and derived patient-level artifacts are intentionally absent: source/cleaned/imputed/derived CSVs, VisitID values, row-level outcomes/predictors, fold assignments, OOF prediction files, bootstrap rows, patient-level SHAP values/local explanations, serialized models/preprocessors/calibrators, notebook outputs, and embedded result images.

## Limits of data-free reproducibility

The code can be **inspected** without authorization. Execution of data-dependent cells is conditional on separately authorized access to the restricted cohort and locally generated artifacts. **This repository does not make the reported numerical results fully reproducible without data.** Internally validated OOF estimates and descriptive full-cohort refits are distinct and must not be conflated.

## Draft manuscript wording (replace only owner-approved placeholders)

> Code availability: The complete analytical code, including output-free notebooks for data preprocessing, sample-size and complexity assessment, internally validated model development, exploratory algorithm benchmarking, robustness and missingness analyses, model packaging, and SHAP-based explanation audits, is available at [REPOSITORY URL], archived as [DOI OR RELEASE IDENTIFIER], commit [COMMIT HASH]. Participant-level data and derived patient-level artifacts are not included because their redistribution is restricted by ethical and data-governance requirements. Consequently, the repository supports inspection of the complete analytical workflow, whereas numerical reproduction requires separately authorized access to the source data.

Do not replace placeholders with invented values. `CITATION.cff` also contains owner-action placeholders.
