# Changelog

## Unreleased — private journal-review construction

### Repository added
* Complete 58-file supplied package: 13 output-free notebooks, frozen protocols, reusable components, utilities, audits and original requirements.
* Reviewer documentation: `README.md`, `docs/REVIEWER_GUIDE.md`, `docs/NOTEBOOK_MAPPING.md`, data/code availability statements, reproducibility notes, schema template, security/contributing guidance and citation placeholders.
* Data-free static tests, pre-commit configuration, CI workflow, Dependabot configuration and privacy audit tooling.

### Portability changes (scientific content unchanged)
* Replaced machine-specific Windows, Linux and Colab absolute paths with environment-variable/`pathlib` resolution (`config/PATH_CONFIGURATION.md`, `.env.example`, `src/ra_paths.py`).
* Kept original requirements files under `environment/original/` and added a consolidated `environment/requirements.txt`.
* Preserved both genuine 03B variants; archived the byte-identical Colab duplicate.

### Privacy-driven changes (no analytical decision changed)
* Removed individual VisitID values and individual-level correction values from `02_data_cleaning_and_preprocessing.ipynb`, `scripts/build_decision_report.py` and `docs/stage2_verification.md`. Stage 2 now loads the correction list from an authorized local JSON specified by `RA_CORRECTIONS_PATH`; the precondition and verification logic is unchanged.
* Redacted rare-record counts in decision-register prose where they functioned as participant examples.
* No data, prediction, SHAP, checkpoint or model artifacts were added.

### Release authorization
* Owner authorized public release to `saeed-soleimani98/RA-Phenotype-Probability-Models`; status banners updated. Push and final metadata placeholders remain owner actions.

### Pending owner decisions
Name/account, license, public status, integrations, author/ethics/funder metadata, DOI/archive and final release tag.
